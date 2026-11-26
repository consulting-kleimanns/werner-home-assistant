"""Grundverbrauch: anerkennen, was der Bewohner schon geschafft hat.

Der Grundverbrauch ist das, was im Haushalt rund um die Uhr läuft: Kühlschrank,
Router, Geräte im Bereitschaftsmodus. Werner misst ihn nachts zwischen 1 und
5 Uhr aus der Zählerstatistik – nur in Nächten, in denen der Bewohner zu Hause
ist (Urlaub zählt nicht).

Grundsätze:

* Anerkennen statt antreiben: Werner zeigt, wie viel seit dem Ausgangswert
  eingespart ist, und vergibt Erfolge, die bleiben.
* Nur kleine, machbare Schritte (etwa 10 Prozent weniger).
* Ab „sehr gut“ gibt es kein neues Ziel mehr – nur noch „Halten genügt“.
  Unter das, was dauernd laufen muss, setzt Werner nie ein Ziel.
* Steigt der Verbrauch, gibt es einen freundlichen Hinweis. Bleibt er vier
  Wochen oben, nimmt Werner das als neuen Normalfall und fragt nicht weiter.

Werte werden je Nacht gespeichert: Der Anwesenheitsverlauf von Home Assistant
reicht meist nur ein paar Tage zurück.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timedelta
import logging
from statistics import median
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_HOME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import CONF_GRID_ENERGY, CONF_PERSON, DOMAIN

_LOGGER = logging.getLogger(__name__)

NIGHT_FROM_H = 1
NIGHT_TO_H = 5
LEVELS = (60, 100, 150)  # Watt: sehr gut / gut / mittel / darüber hoch
LEVEL_NAMES = ("very_good", "good", "medium", "high")
FLOOR_W = 45  # Kühlschrank, Router, Zähler – darunter setzt Werner kein Ziel
STEP = 0.10  # nächster Schritt: etwa 10 Prozent weniger
START_NIGHTS = 14  # so viele Nächte, bis der Ausgangswert feststeht
WEEK_MIN_NIGHTS = 3
RISE_W = 20  # ab so viel mehr als in den Wochen davor gibt es einen Hinweis
RISE_FACTOR = 1.25
WEEKS = 13
BACKFILL_DAYS = 10
KEEP_NIGHTS = 400
DEFAULT_PRICE_CT = 30.0

STORE_VERSION = 1


def level_of(watt: float) -> int:
    for i, limit in enumerate(LEVELS):
        if watt <= limit:
            return i
    return len(LEVELS)


def _round5(value: float) -> int:
    return int(round(value / 5) * 5)


def evaluate(nights: dict[str, float | None], start: dict[str, Any] | None, last: date) -> dict[str, Any]:
    """Wochenwerte, Stufe, Ziel und Hinweis aus den gespeicherten Nächten (ohne Seiteneffekte)."""
    weeks: list[dict[str, Any]] = []
    for k in range(WEEKS - 1, -1, -1):
        end = last - timedelta(days=7 * k)
        days = [end - timedelta(days=d) for d in range(7)]
        values = [nights[d.isoformat()] for d in days if nights.get(d.isoformat()) is not None]
        weeks.append(
            {
                "end": end.isoformat(),
                "w": round(median(values)) if len(values) >= WEEK_MIN_NIGHTS else None,
                "nights": len(values),
            }
        )
    current = weeks[-1]["w"]
    valid = sorted((d, v) for d, v in nights.items() if v is not None)
    result: dict[str, Any] = {
        "weeks": weeks,
        "current_w": current,
        "start_w": start["w"] if start else None,
        "start_date": start["date"] if start else None,
        "learning": start is None,
        "nights_valid": len(valid),
        "nights_needed": START_NIGHTS,
        "levels": list(LEVELS),
        "floor_w": FLOOR_W,
        "level": None,
        "goal_w": None,
        "done": False,
        "rise": None,
        "saved_w": None,
    }
    if current is None:
        return result
    lvl = level_of(current)
    result["level"] = LEVEL_NAMES[lvl]
    result["done"] = lvl == 0
    if not result["done"]:
        result["goal_w"] = max(_round5(current * (1 - STEP)), FLOOR_W)
    if start:
        result["saved_w"] = round(start["w"] - current)
    before = [w["w"] for w in weeks[-5:-1] if w["w"] is not None]
    if before:
        ref = median(before)
        if current >= ref + RISE_W and current >= ref * RISE_FACTOR:
            result["rise"] = {"from_w": round(ref), "by_w": round(current - ref)}
            # Zurück auf den Wert davor – aber nie tiefer als das letzte Ziel.
            result["goal_w"] = max(_round5(ref), FLOOR_W) if not result["done"] else None
    return result


def new_wins(state: dict[str, Any], start: dict[str, Any] | None, wins: dict[str, str]) -> dict[str, str]:
    """Erfolge, die jetzt neu erreicht sind. Einmal erreicht, bleiben sie."""
    today = dt_util.now().date().isoformat()
    current = state["current_w"]
    found: dict[str, str] = {}
    if current is None:
        return found
    if start and current <= start["w"] - 10:
        found["minus_10"] = today
    if start and start["w"] > LEVELS[1] and current <= LEVELS[1]:
        found["good"] = today
    if current <= LEVELS[0]:
        found["very_good"] = today
    recent = [w["w"] for w in state["weeks"]]
    for weeks_needed, key in ((4, "held_4"), (12, "held_12")):
        tail = recent[-weeks_needed:]
        if len(tail) == weeks_needed and all(v is not None and v <= LEVELS[0] for v in tail):
            found[key] = today
    return {k: v for k, v in found.items() if k not in wins}


class Grundverbrauch:
    """Nächte messen, speichern und für „Mein Zuhause“ bewerten."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.grundverbrauch.{entry.entry_id}")
        self.data: dict[str, Any] = {"nights": {}, "start": None, "wins": {}}
        self._unsub: Callable[[], None] | None = None

    async def async_start(self) -> None:
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            self.data.update({k: stored.get(k, v) for k, v in self.data.items()})
        self._unsub = async_track_time_change(self.hass, self._nightly, hour=NIGHT_TO_H, minute=20, second=0)
        self.hass.async_create_background_task(self.async_update(), f"{DOMAIN}_grundverbrauch")

    @callback
    def stop(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    @callback
    def _nightly(self, _now: datetime) -> None:
        self.hass.async_create_background_task(self.async_update(), f"{DOMAIN}_grundverbrauch")

    def _last_night(self) -> date:
        """Die letzte abgeschlossene Nacht (benannt nach dem Morgen)."""
        now = dt_util.now()
        day = now.date()
        return day if now.hour >= NIGHT_TO_H else day - timedelta(days=1)

    async def async_update(self) -> None:
        """Fehlende Nächte nachtragen, Ausgangswert und Erfolge festhalten."""
        statistic_id = self.entry.options.get(CONF_GRID_ENERGY)
        person = self.entry.data.get(CONF_PERSON)
        if not statistic_id or not person:
            return
        last = self._last_night()
        nights: dict[str, float | None] = self.data["nights"]
        todo = [
            last - timedelta(days=d)
            for d in range(BACKFILL_DAYS)
            if (last - timedelta(days=d)).isoformat() not in nights
        ]
        if todo:
            measured = await self._measure(sorted(todo), statistic_id, person)
            nights.update(measured)
        if len(nights) > KEEP_NIGHTS:
            for key in sorted(nights)[: len(nights) - KEEP_NIGHTS]:
                nights.pop(key)
        valid = sorted((d, v) for d, v in nights.items() if v is not None)
        if self.data["start"] is None and len(valid) >= START_NIGHTS:
            first = valid[:START_NIGHTS]
            self.data["start"] = {"w": round(median(v for _, v in first)), "date": first[-1][0]}
        state = evaluate(nights, self.data["start"], last)
        self.data["wins"].update(new_wins(state, self.data["start"], self.data["wins"]))
        await self._store.async_save(self.data)

    async def _measure(self, days: list[date], statistic_id: str, person: str) -> dict[str, float | None]:
        """Grundverbrauch je Nacht in Watt; None = nicht zu Hause. Ohne Daten: nicht eingetragen."""
        try:
            from homeassistant.components.recorder import get_instance, history  # noqa: PLC0415
            from homeassistant.components.recorder.statistics import statistics_during_period  # noqa: PLC0415
        except ImportError:
            return {}
        if "recorder" not in self.hass.config.components:
            return {}
        tz = dt_util.get_default_time_zone()
        first = datetime.combine(days[0], datetime.min.time(), tz).replace(hour=NIGHT_FROM_H)
        last = datetime.combine(days[-1], datetime.min.time(), tz).replace(hour=NIGHT_TO_H)
        recorder = get_instance(self.hass)
        try:
            stats = await recorder.async_add_executor_job(
                statistics_during_period,
                self.hass,
                dt_util.as_utc(first),
                dt_util.as_utc(last),
                {statistic_id},
                "hour",
                None,
                {"change"},
            )
            states = await recorder.async_add_executor_job(
                lambda: history.state_changes_during_period(
                    self.hass, dt_util.as_utc(first), dt_util.as_utc(last), person, include_start_time_state=True
                )
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Grundverbrauch: keine Daten (%s)", err)
            return {}

        per_hour: dict[datetime, float] = {}
        for row in stats.get(statistic_id) or []:
            begin, change = row.get("start"), row.get("change")
            if begin is None or change is None:
                continue
            ts = dt_util.as_local(dt_util.utc_from_timestamp(begin) if isinstance(begin, (int, float)) else begin)
            per_hour[ts.replace(minute=0, second=0, microsecond=0)] = max(0.0, float(change)) * 1000

        presence = sorted(
            (s.last_changed, s.state) for s in (states.get(person) or states.get(person.lower()) or [])
        )
        result: dict[str, float | None] = {}
        for day in days:
            start = datetime.combine(day, datetime.min.time(), tz).replace(hour=NIGHT_FROM_H)
            end = start.replace(hour=NIGHT_TO_H)
            hours = [start + timedelta(hours=h) for h in range(NIGHT_TO_H - NIGHT_FROM_H)]
            values = [per_hour[h] for h in hours if h in per_hour]
            if len(values) < len(hours):
                continue  # Zähler lückenhaft: lieber nicht werten
            before = [st for ts, st in presence if ts <= start]
            during = [st for ts, st in presence if start < ts < end]
            if not before and not during:
                continue  # kein Anwesenheitsverlauf mehr vorhanden
            at_start = before[-1] if before else during[0]
            home = at_start == STATE_HOME and all(st == STATE_HOME for st in during)
            result[day.isoformat()] = round(median(values), 1) if home else None
        return result

    async def async_model(self, price_ct: float | None) -> dict[str, Any]:
        """Alles, was „Mein Zuhause“ zum Grundverbrauch anzeigt."""
        state = evaluate(self.data["nights"], self.data["start"], self._last_night())
        price = price_ct if price_ct else DEFAULT_PRICE_CT
        def euro(watt: float | None) -> int | None:
            return None if watt is None else round(watt * 8.76 * price / 100)
        order = ["minus_10", "good", "very_good", "held_4", "held_12"]
        wins = sorted(self.data["wins"].items(), key=lambda kv: (kv[1], order.index(kv[0]) if kv[0] in order else 99))
        return {
            **state,
            "configured": bool(self.entry.options.get(CONF_GRID_ENERGY)),
            "price_ct": round(price, 1),
            "price_assumed": not price_ct,
            "cost_eur_year": euro(state["current_w"]),
            "saved_eur_year": euro(state["saved_w"]) if (state["saved_w"] or 0) > 0 else None,
            "wins": [{"key": k, "date": d} for k, d in wins],
        }
