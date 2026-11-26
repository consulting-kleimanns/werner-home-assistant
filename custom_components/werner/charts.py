"""Daten für die Diagramme in „Mein Zuhause“ › Energie.

Drei Reihen, jede freiwillig:

* Strompreis von 6 Stunden zurück bis 24 Stunden voraus – aus der eingebauten
  Integration „Nord Pool“ (Börsenpreis, ohne Konto). Auf Wunsch mit
  Mehrwertsteuer und einem festen Aufschlag für Netzentgelt und Abgaben.
* Sonnenstrom-Vorhersage für heute und morgen – aus der eingebauten
  Integration „Forecast.Solar“.
* Stromverbrauch der Wohnung: die letzten 12 Stunden aus der Statistik von
  Home Assistant, dazu eine Vorhersage für die nächsten 6 Stunden aus dem
  Durchschnitt derselben Uhrzeit an den vergangenen Tagen.

Alles bleibt lokal; Werner fragt keine fremden Dienste selbst an.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    CONF_GRID_ENERGY,
    CONF_PRICE_ENTRY,
    CONF_PRICE_MARKUP,
    CONF_PRICE_VAT,
    CONF_PV_FORECAST,
)

_LOGGER = logging.getLogger(__name__)

PRICE_BACK_H = 6
PRICE_AHEAD_H = 24
USE_BACK_H = 12
USE_AHEAD_H = 6
USE_HISTORY_DAYS = 14
VAT = 0.19


def _loaded(hass: HomeAssistant, domain: str) -> list[ConfigEntry]:
    return [
        e for e in hass.config_entries.async_entries(domain) if e.state is ConfigEntryState.LOADED
    ]


def price_entries(hass: HomeAssistant) -> list[dict[str, str]]:
    """Nord-Pool-Einträge zur Auswahl."""
    return [{"entry_id": e.entry_id, "title": e.title or "Nord Pool"} for e in _loaded(hass, "nordpool")]


def pv_forecasts(hass: HomeAssistant) -> list[dict[str, str]]:
    """Forecast.Solar-Einträge zur Auswahl."""
    return [
        {"entry_id": e.entry_id, "title": e.title or "Forecast.Solar"}
        for e in _loaded(hass, "forecast_solar")
    ]


def _pick(options: dict[str, Any], key: str, choices: list[dict[str, str]]) -> str | None:
    """Gewählten Eintrag nehmen – oder den einzigen vorhandenen."""
    chosen = options.get(key)
    ids = [c["entry_id"] for c in choices]
    if chosen == "off":
        return None
    if chosen in ids:
        return chosen
    return ids[0] if len(ids) == 1 else None


def _hour(ts: datetime) -> datetime:
    return ts.replace(minute=0, second=0, microsecond=0)


async def _prices(hass: HomeAssistant, entry_id: str, options: dict[str, Any]) -> dict[str, Any] | None:
    now = dt_util.now()
    start, end = _hour(now) - timedelta(hours=PRICE_BACK_H), _hour(now) + timedelta(hours=PRICE_AHEAD_H)
    buckets: dict[datetime, list[float]] = defaultdict(list)
    day = start.date()
    while day <= end.date():
        try:
            res = await hass.services.async_call(
                "nordpool",
                "get_prices_for_date",
                {"config_entry": entry_id, "date": day.isoformat()},
                blocking=True,
                return_response=True,
            )
        except Exception as err:  # noqa: BLE001 – morgen gibt es erst ab Mittag
            _LOGGER.debug("Keine Preise für %s: %s", day, err)
            res = None
        for rows in (res or {}).values():
            for row in rows if isinstance(rows, list) else []:
                ts = dt_util.parse_datetime(str(row.get("start", "")))
                price = row.get("price")
                if ts is None or price is None:
                    continue
                ts = _hour(dt_util.as_local(ts))
                if start <= ts < end:
                    buckets[ts].append(float(price))
            break  # nur das erste Gebiet
        day += timedelta(days=1)
    if not buckets:
        return None

    vat = bool(options.get(CONF_PRICE_VAT, True))
    markup = float(options.get(CONF_PRICE_MARKUP) or 0)
    points = []
    for ts in sorted(buckets):
        ct = sum(buckets[ts]) / len(buckets[ts]) / 10  # €/MWh → ct/kWh
        if vat:
            ct *= 1 + VAT
        points.append({"t": ts.isoformat(), "v": round(ct + markup, 1)})
    label = "Ihr Strompreis (geschätzt)" if markup else (
        "Börsenpreis inkl. Mehrwertsteuer" if vat else "Börsenpreis"
    )
    return {"unit": "ct/kWh", "label": label, "points": points, "markup": markup, "vat": vat}


async def _pv(hass: HomeAssistant, entry_id: str) -> dict[str, Any] | None:
    try:
        from homeassistant.components.forecast_solar.energy import async_get_solar_forecast
    except ImportError:
        return None
    try:
        data = await async_get_solar_forecast(hass, entry_id)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Keine Sonnen-Vorhersage: %s", err)
        return None
    wh = (data or {}).get("wh_hours") or {}
    now = dt_util.now()
    start, end = _hour(now), _hour(now) + timedelta(hours=PRICE_AHEAD_H)
    points, per_day = [], defaultdict(float)
    for key, value in wh.items():
        ts = dt_util.parse_datetime(str(key))
        if ts is None:
            continue
        ts = dt_util.as_local(ts)
        per_day[ts.date().isoformat()] += float(value) / 1000
        if start <= _hour(ts) < end:
            points.append({"t": _hour(ts).isoformat(), "v": round(float(value) / 1000, 2)})
    if not points and not per_day:
        return None
    points.sort(key=lambda p: p["t"])
    today = now.date()
    return {
        "unit": "kWh",
        "points": points,
        "today_kwh": round(per_day.get(today.isoformat(), 0.0), 1),
        "tomorrow_kwh": round(per_day.get((today + timedelta(days=1)).isoformat(), 0.0), 1),
    }


async def _use(hass: HomeAssistant, statistic_id: str) -> dict[str, Any] | None:
    try:
        from homeassistant.components.recorder import get_instance
        from homeassistant.components.recorder.statistics import statistics_during_period
    except ImportError:
        return None
    if "recorder" not in hass.config.components:
        return None
    now = dt_util.now()
    this_hour = _hour(now)
    start = this_hour - timedelta(days=USE_HISTORY_DAYS)
    try:
        stats = await get_instance(hass).async_add_executor_job(
            statistics_during_period,
            hass,
            dt_util.as_utc(start),
            dt_util.as_utc(this_hour + timedelta(hours=1)),
            {statistic_id},
            "hour",
            None,
            {"change"},
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Keine Verbrauchsstatistik: %s", err)
        return None
    rows = stats.get(statistic_id) or []
    by_hour: dict[datetime, float] = {}
    for row in rows:
        begin = row.get("start")
        change = row.get("change")
        if begin is None or change is None:
            continue
        ts = dt_util.as_local(
            dt_util.utc_from_timestamp(begin) if isinstance(begin, (int, float)) else begin
        )
        by_hour[_hour(ts)] = max(0.0, float(change))
    if not by_hour:
        return None

    past = [
        {"t": ts.isoformat(), "v": round(by_hour[ts], 2)}
        for ts in sorted(by_hour)
        if ts >= this_hour - timedelta(hours=USE_BACK_H)
    ]
    # Vorhersage: Mittel derselben Uhrzeit an den vergangenen Tagen.
    same: dict[int, list[float]] = defaultdict(list)
    for ts, value in by_hour.items():
        if ts < this_hour:
            same[ts.hour].append(value)
    forecast = []
    for step in range(0, USE_AHEAD_H + 1):
        ts = this_hour + timedelta(hours=step)
        values = same.get(ts.hour) or []
        if values:
            forecast.append({"t": ts.isoformat(), "v": round(sum(values) / len(values), 2)})
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today = sum(v for ts, v in by_hour.items() if ts >= midnight)
    days = len({ts.date() for ts in by_hour if ts < midnight})
    return {
        "unit": "kWh",
        "past": past,
        "forecast": forecast,
        "today_kwh": round(today, 1),
        "forecast_kwh": round(sum(p["v"] for p in forecast[1:]), 1),
        "days": days,
    }


async def async_charts(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Alle drei Reihen; was fehlt, ist None."""
    options = entry.options
    result: dict[str, Any] = {"now": dt_util.now().isoformat(), "price": None, "pv": None, "use": None}
    if price_id := _pick(options, CONF_PRICE_ENTRY, price_entries(hass)):
        result["price"] = await _prices(hass, price_id, options)
    if pv_id := _pick(options, CONF_PV_FORECAST, pv_forecasts(hass)):
        result["pv"] = await _pv(hass, pv_id)
    if grid_energy := options.get(CONF_GRID_ENERGY):
        result["use"] = await _use(hass, grid_energy)
    return result


async def async_mean_price(hass: HomeAssistant, entry: ConfigEntry) -> float | None:
    """Mittlerer Strompreis der nächsten Stunden in ct/kWh – für Euro-Angaben."""
    price_id = _pick(entry.options, CONF_PRICE_ENTRY, price_entries(hass))
    if not price_id:
        return None
    data = await _prices(hass, price_id, entry.options)
    points = (data or {}).get("points") or []
    return sum(p["v"] for p in points) / len(points) if points else None
