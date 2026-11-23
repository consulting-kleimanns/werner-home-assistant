"""Werners Ablauf für einen Bewohner.

Aktivität erkennen, Regeln prüfen, zuerst den Bewohner fragen und erst dann
die Vertrauenspersonen nacheinander informieren. Ein laufender Ablauf wird
nach einem Neustart von Home Assistant fortgesetzt.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_HOME, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from .const import (
    ACTION_FALSE_ALARM,
    ACTIVITY_LOG_MINUTES,
    ACTION_HELP,
    ACTION_NEXT,
    ACTION_OK,
    ACTION_TAKE,
    CHECK_INTERVAL_MINUTES,
    CONF_BASELOAD,
    CONF_NAME,
    CONF_NOTIFY,
    CONF_PERSON,
    CONF_SOURCES,
    CONTACT_WAIT_MINUTES,
    DAY_END_HOUR,
    DAY_START_HOUR,
    DEFAULT_BASELOAD,
    DEFAULT_SETTINGS,
    ENERGY_ENTITY_KEYS,
    CONF_PV_KWP,
    CONF_VEHICLE_NAME,
    EVENT_NOTIFICATION_ACTION,
    MORNING_FROM_HOUR,
    MORNING_LATEST_HOUR,
    NIGHT_END_HOUR,
    NIGHT_START_HOUR,
    PERSON_COUNT,
    STATUS_ASKING,
    STATUS_HELP,
    STATUS_INFORMED,
    STATUS_OK,
    STATUS_PAUSED,
    STATUSES,
    WAY_APP,
    WAY_MAIL,
    WAY_OFF,
    WAY_SIGNAL,
    signal_update,
)

_LOGGER = logging.getLogger(__name__)

# Ein Anstieg um so viele Watt über der Grundlast zählt ebenfalls als Aktivität.
JUMP_W = 200

PROC_ASK = "ask"
PROC_ESCALATE = "escalate"

WAY_LABELS = {WAY_SIGNAL: "Signal", WAY_MAIL: "E-Mail"}

_BAD_STATES = (STATE_UNAVAILABLE, STATE_UNKNOWN)


class Bewohner:
    """Zustand, Einstellungen und Ablauf für einen Bewohner."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.name: str = entry.data[CONF_NAME]
        self.person: str = entry.data[CONF_PERSON]
        self.notify: str = entry.data.get(CONF_NOTIFY) or ""

        self.settings: dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.status: str = STATUS_OK
        self.reason: str = ""
        self.procedure: str | None = None
        self.person_index: int = 0
        self.last_activity: datetime | None = None

        self.entity_ids: dict[str, str] = {}
        self._activity_logged: dict[str, datetime] = {}

        self._started = False
        self._task: asyncio.Task | None = None
        self._unsubs: list[Callable[[], None]] = []
        self._source_unsub: Callable[[], None] | None = None

    # ------------------------------------------------------------------ Hilfen

    @property
    def sources(self) -> list[str]:
        """Aktivitätsquellen aus den Optionen."""
        return list(self.entry.options.get(CONF_SOURCES, []))

    @property
    def baseload(self) -> float:
        """Grundlast in Watt: erst darüber zählt Strom als Aktivität."""
        return float(self.entry.options.get(CONF_BASELOAD, DEFAULT_BASELOAD))

    @property
    def energy(self) -> dict[str, Any]:
        """Optionale Energie- und Auto-Einstellungen für die Oberfläche."""
        options = self.entry.options
        data: dict[str, Any] = {key: options.get(key) for key in ENERGY_ENTITY_KEYS}
        data[CONF_PV_KWP] = options.get(CONF_PV_KWP)
        data[CONF_VEHICLE_NAME] = options.get(CONF_VEHICLE_NAME)
        return data

    @property
    def busy(self) -> bool:
        """Läuft gerade eine Nachfrage oder Eskalation?"""
        return self._task is not None and not self._task.done()

    def person_settings(self, n: int) -> dict[str, str]:
        """Einstellungen der Vertrauensperson n (1–3)."""
        return {
            "name": str(self.settings.get(f"person_{n}_name") or "").strip(),
            "way": str(self.settings.get(f"person_{n}_way") or WAY_OFF),
            "contact": str(self.settings.get(f"person_{n}_contact") or "").strip(),
            "phone": str(self.settings.get(f"person_{n}_phone") or "").strip(),
            "e_mail": str(self.settings.get(f"person_{n}_e_mail") or "").strip(),
        }

    def _is_home(self) -> bool:
        state = self.hass.states.get(self.person)
        return state is not None and state.state == STATE_HOME

    @callback
    def _changed(self) -> None:
        async_dispatcher_send(self.hass, signal_update(self.entry.entry_id))

    @callback
    def log(self, message: str) -> None:
        """Ins Logbuch schreiben (sichtbar im Protokoll des Dashboards)."""
        _LOGGER.info("%s: %s", self.name, message)
        if self.hass.services.has_service("logbook", "log"):
            data = {"name": "Werner", "message": f"{self.name}: {message}"}
            if status_entity := self.entity_ids.get("status"):
                # Am Status-Sensor des Bewohners: so zeigt die Oberfläche nur sein Protokoll.
                data["entity_id"] = status_entity
            self.hass.async_create_task(self.hass.services.async_call("logbook", "log", data))

    @callback
    def _set_status(self, status: str, reason: str | None = None) -> None:
        self.status = status
        if reason is not None:
            self.reason = reason
        self._changed()

    @callback
    def mark_activity(self, when: datetime | None = None) -> None:
        """Aktivität des Bewohners merken."""
        self.last_activity = when or dt_util.utcnow()
        self._changed()

    # --------------------------------------------- Wiederherstellen nach Neustart

    @callback
    def restore_setting(self, key: str, value: Any) -> None:
        """Gespeicherten Wert einer Einstellung übernehmen, ohne Nebenwirkungen."""
        if key in self.settings and value is not None:
            self.settings[key] = value

    @callback
    def restore_status(self, status: str, attributes: dict[str, Any]) -> None:
        """Gespeicherten Status und laufenden Ablauf übernehmen."""
        if status in STATUSES:
            self.status = status
        self.reason = str(attributes.get("reason") or "")
        procedure = attributes.get("procedure")
        self.procedure = procedure if procedure in (PROC_ASK, PROC_ESCALATE) else None
        try:
            self.person_index = int(attributes.get("person_index") or 0)
        except (TypeError, ValueError):
            self.person_index = 0

    @callback
    def restore_last_activity(self, value: datetime | None) -> None:
        """Gespeicherte letzte Aktivität übernehmen."""
        if value is not None:
            self.last_activity = value

    # ------------------------------------------------------------ Start / Stopp

    async def async_start(self) -> None:
        """Nach dem Wiederherstellen aller Entitäten starten."""
        self._started = True
        self._subscribe_sources()
        self._unsubs.append(
            async_track_time_interval(
                self.hass, self._async_check_rules, timedelta(minutes=CHECK_INTERVAL_MINUTES)
            )
        )

        if self.settings["paused"]:
            self.status = STATUS_PAUSED
            self.procedure = None
        elif self.procedure == PROC_ASK:
            self.log("macht nach einem Neustart mit der Nachfrage weiter.")
            self._start(self._ask(self.reason or "Werner fragt nach."))
        elif self.procedure == PROC_ESCALATE:
            self.log("macht nach einem Neustart mit der Benachrichtigung weiter.")
            self._start(self._escalate(self.reason, max(1, self.person_index)))
        elif self.status == STATUS_PAUSED:
            self.status = STATUS_OK
        self._changed()

    @callback
    def stop(self) -> None:
        """Alles beenden (Entfernen oder Neuladen des Eintrags)."""
        self._cancel()
        if self._source_unsub:
            self._source_unsub()
            self._source_unsub = None
        while self._unsubs:
            self._unsubs.pop()()

    @callback
    def options_updated(self) -> None:
        """Aktivitätsquellen oder Energie-Sensoren haben sich geändert."""
        self._subscribe_sources()
        self._changed()

    # ------------------------------------------------------------- Aktivität

    @callback
    def _subscribe_sources(self) -> None:
        if self._source_unsub:
            self._source_unsub()
        entity_ids = sorted(set(self.sources) | {self.person})
        self._source_unsub = async_track_state_change_event(
            self.hass, entity_ids, self._source_changed
        )

    @callback
    def _source_changed(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        if new is None or old is None:
            return
        if new.state in _BAD_STATES or old.state in _BAD_STATES or new.state == old.state:
            return

        if new.entity_id == self.person:
            self.mark_activity()
            if new.state == STATE_HOME:
                self.log("ist wieder zu Hause.")
            elif old.state == STATE_HOME:
                self.log("ist unterwegs – Werner schweigt.")
            return

        if not self._is_activity(old.state, new.state):
            return
        self.mark_activity()
        self._log_activity(new.entity_id, new.name)
        self._check_night()

    @callback
    def _log_activity(self, entity_id: str, label: str) -> None:
        """Aktivität einer Quelle höchstens alle 30 Minuten ins Protokoll schreiben."""
        now = dt_util.utcnow()
        last = self._activity_logged.get(entity_id)
        if last and now - last < timedelta(minutes=ACTIVITY_LOG_MINUTES):
            return
        self._activity_logged[entity_id] = now
        self.log(f"Aktivität bemerkt: {label}")

    def _is_activity(self, old: str, new: str) -> bool:
        """Zahlen (z. B. Leistung in W) zählen nur über der Grundlast."""
        try:
            old_v, new_v = float(old), float(new)
        except ValueError:
            return True
        base = self.baseload
        return new_v > base and (old_v <= base or new_v - old_v >= JUMP_W)

    # ---------------------------------------------------------------- Regeln

    def _may_ask(self) -> bool:
        return (
            not self.settings["paused"]
            and self.status == STATUS_OK
            and not self.busy
            and self._is_home()
            and bool(self.sources)
        )

    @callback
    def _check_night(self) -> None:
        now = dt_util.now()
        if not NIGHT_START_HOUR <= now.hour < NIGHT_END_HOUR:
            return
        if self.settings["rule_night"] and self._may_ask():
            self.ask("Es ist mitten in der Nacht und Werner hat Aktivität bemerkt.")

    async def _async_check_rules(self, _now: datetime | None = None) -> None:
        if not self._may_ask():
            return
        local = dt_util.now()
        last = self.last_activity

        if (
            self.settings["rule_morning"]
            and MORNING_FROM_HOUR <= local.hour < MORNING_LATEST_HOUR
            and local.hour >= int(self.settings["morning_until"])
        ):
            five = local.replace(hour=MORNING_FROM_HOUR, minute=0, second=0, microsecond=0)
            if last is None or last < five:
                self.ask(
                    f"Es ist schon {local:%H:%M} Uhr und Werner hat heute noch nichts von Ihnen bemerkt."
                )
                return

        if self.settings["rule_quiet"] and DAY_START_HOUR <= local.hour < DAY_END_HOUR and last:
            hours = (dt_util.utcnow() - last).total_seconds() / 3600
            if hours >= float(self.settings["quiet_hours"]):
                self.ask(f"Seit etwa {round(hours)} Stunden war es bei Ihnen ganz still.")

    # --------------------------------------------------------- Bedienung

    @callback
    def ask(self, reason: str) -> None:
        """Beim Bewohner nachfragen (nie, wenn Werner pausiert ist)."""
        if self.settings["paused"]:
            return
        self._start(self._ask(reason))

    @callback
    def all_good(self) -> None:
        """Knopf „Alles gut“: laufenden Ablauf beenden, Aktivität merken."""
        self._cancel()
        self.procedure = None
        self.person_index = 0
        self.last_activity = dt_util.utcnow()
        self._set_status(STATUS_PAUSED if self.settings["paused"] else STATUS_OK, "")
        self.log("hat bestätigt: alles gut.")

    @callback
    def help(self) -> None:
        """Knopf „Ich brauche Hilfe“: sofort informieren – auch wenn pausiert."""
        reason = f"{self.name} hat „Ich brauche Hilfe“ gedrückt."
        self._cancel()
        self._set_status(STATUS_HELP, reason)
        self.log("hat „Ich brauche Hilfe“ gedrückt.")
        self._start(self._escalate(reason, 1))

    @callback
    def set_setting(self, key: str, value: Any) -> None:
        """Einstellung ändern (aus den Entitäten)."""
        old = self.settings.get(key)
        self.settings[key] = value
        if key == "paused" and self._started and bool(old) != bool(value):
            if value:
                self._cancel()
                self.procedure = None
                self.person_index = 0
                self.status = STATUS_PAUSED
                self.log("wurde pausiert.")
            else:
                self.status = STATUS_OK
                self.last_activity = dt_util.utcnow()
                self.log("passt wieder auf.")
        self._changed()

    # ------------------------------------------------------------ Ablauf

    @callback
    def _start(self, coro: Coroutine[Any, Any, None]) -> None:
        self._cancel()
        self._task = self.entry.async_create_background_task(
            self.hass, coro, f"werner_{self.entry.entry_id}"
        )

    @callback
    def _cancel(self) -> None:
        if self._task is not None and not self._task.done():
            self._task.cancel()
        self._task = None

    async def _ask(self, reason: str) -> None:
        self.procedure = PROC_ASK
        self.person_index = 0
        self._set_status(STATUS_ASKING, reason)
        wait = int(self.settings["wait_minutes"])
        self.log(f"fragt nach: {reason}")

        tag = f"werner_{self.entry.entry_id}_{int(time.time())}"
        ok_action, help_action = f"{ACTION_OK}_{tag}", f"{ACTION_HELP}_{tag}"
        if self.notify:
            await self._notify(
                self.notify,
                "Werner: Ist alles in Ordnung?",
                f"{reason} Ohne Antwort informiere ich in {wait} Minuten Ihre Vertrauensperson.",
                actions=[
                    (ok_action, "Ja, alles gut", False),
                    (help_action, "Bitte Hilfe holen", True),
                ],
                tag=tag,
            )

        answer = await self._wait_for_action(
            {ok_action: "ok", help_action: "help"}, wait * 60
        )
        if answer == "ok":
            self.procedure = None
            self.last_activity = dt_util.utcnow()
            self._set_status(STATUS_OK, "")
            self.log("hat bestätigt: alles gut.")
            return
        if answer == "help":
            reason = f"{self.name} hat über Werner um Hilfe gebeten."
            self._set_status(STATUS_HELP, reason)
            self.log("hat Hilfe angefordert.")
        else:
            reason = f"{reason} {self.name} hat auf Werners Nachfrage nicht geantwortet."
            self.log(f"hat nicht innerhalb von {wait} Minuten geantwortet.")
        await self._escalate(reason, 1)

    async def _escalate(self, reason: str, start: int) -> None:
        self.procedure = PROC_ESCALATE
        if self.status != STATUS_HELP:
            self._set_status(STATUS_INFORMED, reason)
        else:
            self.reason = reason

        for n in range(start, PERSON_COUNT + 1):
            self.person_index = n
            self._changed()
            person = self.person_settings(n)
            if not person["name"] or person["way"] == WAY_OFF:
                continue
            result = await self._contact(n, person, reason)
            if result == "take":
                self.procedure = None
                self.person_index = 0
                self.log(f"{person['name']} kümmert sich.")
                if self.notify:
                    await self._notify(
                        self.notify, "Werner", f"{person['name']} weiß Bescheid und kümmert sich."
                    )
                self._changed()
                return
            if result == "false_alarm":
                self.procedure = None
                self.person_index = 0
                self.last_activity = dt_util.utcnow()
                self._set_status(STATUS_OK, "")
                self.log(f"{person['name']}: Fehlalarm, alles gut.")
                return
            self.log(f"{person['name']} hat nicht geantwortet oder kann nicht – nächste Person.")

        self.procedure = None
        self.person_index = 0
        self.log(f"Niemand aus der Liste hat übernommen. Grund: {reason}")
        if self.notify:
            await self._notify(
                self.notify,
                "Werner",
                "Ich konnte niemanden aus Ihrer Liste erreichen. "
                "Wenn Sie Hilfe brauchen, rufen Sie bitte 112 an.",
                urgent=True,
            )
        self._changed()

    async def _contact(self, n: int, person: dict[str, str], reason: str) -> str | None:
        """Eine Vertrauensperson informieren. Antwort: take, false_alarm, next oder None."""
        if person["way"] != WAY_APP:
            label = WAY_LABELS.get(person["way"], person["way"])
            self.log(
                f"{person['name']} sollte per {label} informiert werden – dieser Weg kommt "
                "in einer der nächsten Versionen. Nächste Person."
            )
            return None
        if not person["contact"]:
            self.log(
                f"{person['name']}: kein Gerät für die Home-Assistant-App eingetragen – nächste Person."
            )
            return None

        tag = f"werner_{self.entry.entry_id}_{n}_{int(time.time())}"
        take, false_alarm, nxt = (
            f"{ACTION_TAKE}_{tag}",
            f"{ACTION_FALSE_ALARM}_{tag}",
            f"{ACTION_NEXT}_{tag}",
        )
        title = (
            f"Werner: {self.name} braucht Hilfe"
            if self.status == STATUS_HELP
            else f"Werner: {self.name} antwortet nicht"
        )
        self.log(f"informiert {person['name']} (Platz {n}) per Home-Assistant-App.")
        sent = await self._notify(
            person["contact"],
            title,
            f"{reason} Sie sind Vertrauensperson Nr. {n} von {self.name}. "
            f"Bitte antworten Sie. Ohne Antwort informiert Werner in {CONTACT_WAIT_MINUTES} "
            "Minuten die nächste Person. Im Notfall: 112.",
            actions=[
                (take, "1 · Ich kümmere mich", False),
                (false_alarm, "2 · Fehlalarm", False),
                (nxt, "3 · Kann nicht", False),
            ],
            tag=tag,
            urgent=True,
        )
        if not sent:
            return None
        return await self._wait_for_action(
            {take: "take", false_alarm: "false_alarm", nxt: "next"}, CONTACT_WAIT_MINUTES * 60
        )

    async def async_test_person(self, n: int) -> dict[str, Any]:
        """Test-Nachricht an Vertrauensperson n schicken (Knopf in „Einstellen“)."""
        person = self.person_settings(n)
        if not person["name"]:
            return {"ok": False, "text": "Für diese Person ist noch kein Name eingetragen."}
        if person["way"] == WAY_OFF:
            return {"ok": False, "text": "Für diese Person ist „Nicht melden“ gewählt."}
        if person["way"] != WAY_APP:
            label = WAY_LABELS.get(person["way"], person["way"])
            return {"ok": False, "text": f"{label} kommt in einer der nächsten Versionen."}
        if not person["contact"]:
            return {"ok": False, "text": "Für diese Person ist kein App-Gerät eingetragen."}
        sent = await self._notify(
            person["contact"],
            "Werner (Test)",
            f"Test von Werner: {self.name} hat Sie als {n}. Vertrauensperson eingetragen. "
            "Das ist nur ein Test – es ist alles in Ordnung.",
        )
        self.log(f"Test-Nachricht an {person['name']}: {'gesendet' if sent else 'fehlgeschlagen'}.")
        if sent:
            return {
                "ok": True,
                "text": "An die Home-Assistant-App gesendet. Fragen Sie kurz nach, ob sie angekommen ist.",
            }
        return {"ok": False, "text": "Konnte nicht gesendet werden. Stimmt das App-Gerät?"}

    async def _wait_for_action(self, actions: dict[str, str], timeout: float) -> str | None:
        """Auf einen Antwortknopf der Home-Assistant-App warten."""
        future: asyncio.Future[str | None] = self.hass.loop.create_future()

        @callback
        def _on_action(event: Event) -> None:
            answer = actions.get(event.data.get("action", ""))
            if answer and not future.done():
                future.set_result(answer)

        @callback
        def _on_timeout(_now: datetime) -> None:
            if not future.done():
                future.set_result(None)

        unsub_event = self.hass.bus.async_listen(EVENT_NOTIFICATION_ACTION, _on_action)
        unsub_timer = async_call_later(self.hass, timeout, _on_timeout)
        try:
            return await future
        finally:
            unsub_event()
            unsub_timer()

    async def _notify(
        self,
        service: str,
        title: str,
        message: str,
        actions: list[tuple[str, str, bool]] | None = None,
        tag: str | None = None,
        urgent: bool = False,
    ) -> bool:
        """Nachricht über einen notify-Dienst der Home-Assistant-App senden."""
        service = service.removeprefix("notify.")
        if not self.hass.services.has_service("notify", service):
            self.log(f"Benachrichtigungsdienst notify.{service} gibt es nicht.")
            return False
        data: dict[str, Any] = {}
        if actions:
            data["actions"] = [
                {"action": action, "title": label, **({"destructive": True} if destructive else {})}
                for action, label, destructive in actions
            ]
        if tag:
            data["tag"] = tag
        if actions or urgent:
            data["push"] = {"interruption-level": "time-sensitive"}
            data.update(
                {"priority": "high", "importance": "high", "ttl": 0, "channel": "werner_alarm"}
            )
        try:
            await self.hass.services.async_call(
                "notify",
                service,
                {"title": title, "message": message, "data": data},
                blocking=True,
            )
        except Exception as err:  # noqa: BLE001 – jede Störung nur protokollieren
            self.log(f"Nachricht über notify.{service} fehlgeschlagen: {err}")
            return False
        return True
