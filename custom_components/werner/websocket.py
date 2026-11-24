"""Selbstbestimmung: Bewohner richten Werner in „Mein Zuhause“ selbst ein.

Diese Befehle brauchen keine Administratorrechte. Es gelten diese Regeln:

- Jeder darf Werner für sich selbst einschalten, ändern und wieder beenden.
- Jeder darf einen weiteren Bewohner des Haushalts eintragen. Werner passt auf
  diese Person aber erst auf, wenn sie selbst zugestimmt hat (mit ihrer eigenen
  Anmeldung). Lehnt sie ab, wird der Eintrag gelöscht.
- Einstellungen anderer Bewohner sieht und ändert niemand außer einem
  Administrator (Helfer). Andere Bewohner erscheinen nur mit Namen.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .signal_messenger import SignalError, get_client

from .const import (
    CONF_BASELOAD,
    CONF_CONSENT,
    CONF_CREATED_BY,
    CONF_NAME,
    CONF_NOTIFY,
    CONF_PERSON,
    CONF_PV_KWP,
    CONF_SOURCES,
    CONF_VEHICLE_NAME,
    DEFAULT_BASELOAD,
    ENERGY_ENTITY_KEYS,
    DOMAIN,
    SOURCE_UI,
)

ERR_NOT_ALLOWED = "not_allowed"
ERR_INVALID = "invalid"


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Befehle für die Oberfläche anmelden."""
    websocket_api.async_register_command(hass, ws_household)
    websocket_api.async_register_command(hass, ws_add)
    websocket_api.async_register_command(hass, ws_update)
    websocket_api.async_register_command(hass, ws_consent)
    websocket_api.async_register_command(hass, ws_remove)
    websocket_api.async_register_command(hass, ws_sources)
    websocket_api.async_register_command(hass, ws_set_sources)
    websocket_api.async_register_command(hass, ws_energy)
    websocket_api.async_register_command(hass, ws_set_energy)
    websocket_api.async_register_command(hass, ws_signal_status)
    websocket_api.async_register_command(hass, ws_signal_qr)


# ------------------------------------------------------------------ Hilfen


def _user_of(hass: HomeAssistant, person: str) -> str | None:
    state = hass.states.get(person)
    return state.attributes.get("user_id") if state else None


def _entries(hass: HomeAssistant) -> list[ConfigEntry]:
    return hass.config_entries.async_entries(DOMAIN)


def _entry(hass: HomeAssistant, entry_id: str) -> ConfigEntry | None:
    entry = hass.config_entries.async_get_entry(entry_id)
    return entry if entry and entry.domain == DOMAIN else None


def _is_own(hass: HomeAssistant, entry: ConfigEntry, user_id: str) -> bool:
    return _user_of(hass, entry.data[CONF_PERSON]) == user_id


def _phones(hass: HomeAssistant) -> list[str]:
    return sorted(s for s in hass.services.async_services_for_domain("notify") if s.startswith("mobile_app_"))


def _clean_notify(hass: HomeAssistant, notify: str | None) -> str | None:
    """Leer ist erlaubt; sonst muss es ein vorhandener notify-Dienst sein."""
    notify = (notify or "").strip().removeprefix("notify.")
    if notify and not hass.services.has_service("notify", notify):
        return None
    return notify


def _user_name(hass: HomeAssistant, user_id: str | None) -> str:
    if not user_id:
        return ""
    for state in hass.states.async_all("person"):
        if state.attributes.get("user_id") == user_id:
            return state.name
    return ""


# ---------------------------------------------------------------- Befehle


@websocket_api.websocket_command({vol.Required("type"): "werner/household"})
@callback
def ws_household(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Haushalt: wer ist eingetragen, wer könnte dazukommen, welche Handys gibt es."""
    user = connection.user
    taken = {e.data[CONF_PERSON] for e in _entries(hass)}
    me = next(
        (s.entity_id for s in hass.states.async_all("person") if s.attributes.get("user_id") == user.id),
        None,
    )
    residents = []
    for entry in _entries(hass):
        own = _is_own(hass, entry, user.id)
        residents.append(
            {
                "entry_id": entry.entry_id,
                "name": entry.data[CONF_NAME],
                "mine": own,
                "consent": bool(entry.data.get(CONF_CONSENT, True)),
                "created_by": _user_name(hass, entry.data.get(CONF_CREATED_BY)),
                "may_remove": own
                or user.is_admin
                or (
                    not entry.data.get(CONF_CONSENT, True)
                    and entry.data.get(CONF_CREATED_BY) == user.id
                ),
                # Eigene Einstellungen sieht jeder; fremde nur der Helfer.
                **(
                    {"person": entry.data[CONF_PERSON], "notify": entry.data.get(CONF_NOTIFY, "")}
                    if own or user.is_admin
                    else {}
                ),
            }
        )
    persons = [
        {
            "entity_id": s.entity_id,
            "name": s.name,
            "has_login": bool(s.attributes.get("user_id")),
            "taken": s.entity_id in taken,
            "me": s.entity_id == me,
        }
        for s in sorted(hass.states.async_all("person"), key=lambda s: s.name)
    ]
    connection.send_result(
        msg["id"],
        {
            "is_admin": user.is_admin,
            "me": me,
            "residents": residents,
            "persons": persons,
            "phones": _phones(hass),
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "werner/resident/add",
        vol.Required("person"): str,
        vol.Required("name"): vol.All(str, vol.Length(min=1, max=40)),
        vol.Optional("notify"): str,
    }
)
@websocket_api.async_response
async def ws_add(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Werner für sich selbst einschalten oder einen weiteren Bewohner eintragen."""
    user = connection.user
    person = msg["person"]
    state = hass.states.get(person)
    if state is None or not person.startswith("person."):
        connection.send_error(msg["id"], ERR_INVALID, "Diese Person gibt es nicht.")
        return
    if any(e.data[CONF_PERSON] == person for e in _entries(hass)):
        connection.send_error(msg["id"], ERR_INVALID, "Für diese Person ist Werner schon eingerichtet.")
        return
    owner = state.attributes.get("user_id")
    if owner is None and not user.is_admin:
        connection.send_error(
            msg["id"], ERR_NOT_ALLOWED,
            "Diese Person hat keine eigene Anmeldung. Das richtet ein Helfer ein.",
        )
        return
    notify = _clean_notify(hass, msg.get("notify"))
    if notify is None:
        connection.send_error(msg["id"], ERR_INVALID, "Dieses Handy gibt es nicht.")
        return

    # Zustimmung: wer sich selbst einträgt, stimmt damit zu. Für andere gilt sie erst,
    # wenn diese Person selbst „Ja“ sagt. Personen ohne Anmeldung trägt nur ein Helfer ein.
    data = {
        CONF_NAME: msg["name"].strip(),
        CONF_PERSON: person,
        CONF_NOTIFY: notify,
        CONF_CONSENT: owner == user.id or owner is None,
        CONF_CREATED_BY: user.id,
    }
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_UI}, data=data)
    if result.get("type") != "create_entry":
        connection.send_error(msg["id"], ERR_INVALID, "Werner konnte nicht eingerichtet werden.")
        return
    if not data[CONF_CONSENT] and notify:
        await hass.services.async_call(
            "notify",
            notify,
            {
                "title": "Werner",
                "message": f"{_user_name(hass, user.id) or 'Jemand'} hat Werner für Sie eingetragen. "
                "Werner passt erst auf, wenn Sie zustimmen. Öffnen Sie dafür „Mein Zuhause“.",
            },
            blocking=False,
        )
    connection.send_result(msg["id"], {"entry_id": result["result"].entry_id, "consent": data[CONF_CONSENT]})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "werner/resident/update",
        vol.Required("entry_id"): str,
        vol.Optional("name"): vol.All(str, vol.Length(min=1, max=40)),
        vol.Optional("notify"): str,
    }
)
@websocket_api.async_response
async def ws_update(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Eigenen Namen oder eigenes Handy ändern."""
    entry = _entry(hass, msg["entry_id"])
    if entry is None or not (connection.user.is_admin or _is_own(hass, entry, connection.user.id)):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Das dürfen nur Sie selbst ändern.")
        return
    data = dict(entry.data)
    if "name" in msg:
        data[CONF_NAME] = msg["name"].strip()
    if "notify" in msg:
        notify = _clean_notify(hass, msg["notify"])
        if notify is None:
            connection.send_error(msg["id"], ERR_INVALID, "Dieses Handy gibt es nicht.")
            return
        data[CONF_NOTIFY] = notify
    if data != dict(entry.data):
        hass.config_entries.async_update_entry(entry, data=data, title=data[CONF_NAME])
        hass.config_entries.async_schedule_reload(entry.entry_id)
    connection.send_result(msg["id"], {})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "werner/resident/consent",
        vol.Required("entry_id"): str,
        vol.Required("accept"): bool,
    }
)
@websocket_api.async_response
async def ws_consent(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Der Bewohner selbst sagt Ja oder Nein. Bei Nein wird alles gelöscht."""
    entry = _entry(hass, msg["entry_id"])
    if entry is None or not _is_own(hass, entry, connection.user.id):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Zustimmen kann nur die Person selbst.")
        return
    if msg["accept"]:
        hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_CONSENT: True})
        hass.config_entries.async_schedule_reload(entry.entry_id)
    else:
        await hass.config_entries.async_remove(entry.entry_id)
    connection.send_result(msg["id"], {})


@websocket_api.websocket_command(
    {vol.Required("type"): "werner/resident/remove", vol.Required("entry_id"): str}
)
@websocket_api.async_response
async def ws_remove(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Werner für sich beenden – oder einen noch nicht bestätigten Eintrag zurücknehmen."""
    user = connection.user
    entry = _entry(hass, msg["entry_id"])
    allowed = entry is not None and (
        user.is_admin
        or _is_own(hass, entry, user.id)
        or (not entry.data.get(CONF_CONSENT, True) and entry.data.get(CONF_CREATED_BY) == user.id)
    )
    if not allowed:
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Das darf nur die Person selbst.")
        return
    await hass.config_entries.async_remove(entry.entry_id)
    connection.send_result(msg["id"], {})


# ---------------------------------------------------- Aktivitätsquellen

# Was als Zeichen für Aktivität taugt – in einfachen Gruppen für die Oberfläche.
MOTION_CLASSES = {"motion", "occupancy", "presence", "door", "opening", "window", "garage_door", "moving", "vibration"}


def _source_group(hass: HomeAssistant, entity_id: str) -> str | None:
    """Gruppe einer möglichen Aktivitätsquelle oder None, wenn sie nicht passt."""
    state = hass.states.get(entity_id)
    if state is None:
        return None
    domain = entity_id.split(".", 1)[0]
    device_class = state.attributes.get("device_class")
    if domain == "sensor" and device_class == "power":
        return "strom"
    if domain == "binary_sensor" and device_class in MOTION_CLASSES:
        return "bewegung"
    if domain == "media_player":
        return "geraete"
    return None


def _own_entity(hass: HomeAssistant, entity_id: str) -> bool:
    entry = er.async_get(hass).async_get(entity_id)
    return entry is not None and entry.platform == DOMAIN


@websocket_api.websocket_command(
    {vol.Required("type"): "werner/sources", vol.Required("entry_id"): str}
)
@callback
def ws_sources(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Welche Geräte Werner beachten könnte – und welche der Bewohner gewählt hat."""
    entry = _entry(hass, msg["entry_id"])
    if entry is None or not (connection.user.is_admin or _is_own(hass, entry, connection.user.id)):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Das dürfen nur Sie selbst sehen.")
        return
    chosen = list(entry.options.get(CONF_SOURCES, []))
    candidates = []
    for state in hass.states.async_all(["sensor", "binary_sensor", "media_player"]):
        group = _source_group(hass, state.entity_id)
        if group is None or _own_entity(hass, state.entity_id):
            continue
        candidates.append(
            {
                "entity_id": state.entity_id,
                "name": state.name,
                "group": group,
                "state": state.state,
                "unit": state.attributes.get("unit_of_measurement", ""),
            }
        )
    # Gewählte Quellen, die nicht in die Gruppen passen (vom Helfer eingetragen), trotzdem zeigen.
    for entity_id in chosen:
        if not any(c["entity_id"] == entity_id for c in candidates):
            state = hass.states.get(entity_id)
            candidates.append(
                {
                    "entity_id": entity_id,
                    "name": state.name if state else entity_id,
                    "group": "andere",
                    "state": state.state if state else "unavailable",
                    "unit": state.attributes.get("unit_of_measurement", "") if state else "",
                }
            )
    candidates.sort(key=lambda c: (c["group"], c["name"].lower()))
    connection.send_result(
        msg["id"],
        {
            "chosen": chosen,
            "baseload_w": entry.options.get(CONF_BASELOAD, DEFAULT_BASELOAD),
            "candidates": candidates,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "werner/resident/sources",
        vol.Required("entry_id"): str,
        vol.Required("sources"): [str],
        vol.Optional("baseload_w"): vol.All(vol.Coerce(float), vol.Range(min=0, max=5000)),
    }
)
@callback
def ws_set_sources(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Der Bewohner bestimmt selbst, worauf Werner achtet."""
    entry = _entry(hass, msg["entry_id"])
    if entry is None or not (connection.user.is_admin or _is_own(hass, entry, connection.user.id)):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Das dürfen nur Sie selbst ändern.")
        return
    already = set(entry.options.get(CONF_SOURCES, []))
    sources = []
    for entity_id in dict.fromkeys(msg["sources"]):
        # Neue Quellen nur aus den passenden Gruppen; Helfer dürfen alles.
        if entity_id in already or connection.user.is_admin or (
            _source_group(hass, entity_id) and not _own_entity(hass, entity_id)
        ):
            sources.append(entity_id)
        else:
            connection.send_error(msg["id"], ERR_INVALID, f"{entity_id} kann Werner nicht beachten.")
            return
    options = {**entry.options, CONF_SOURCES: sources}
    if "baseload_w" in msg:
        options[CONF_BASELOAD] = msg["baseload_w"]
    hass.config_entries.async_update_entry(entry, options=options)
    connection.send_result(msg["id"], {"chosen": sources})


# ------------------------------------------------------- Energie-Anzeige


def _energy_fits(hass: HomeAssistant, key: str, entity_id: str) -> bool:
    """Passt die Entität zu diesem Feld der Energie-Anzeige?"""
    state = hass.states.get(entity_id)
    if state is None or _own_entity(hass, entity_id):
        return False
    domain = entity_id.split(".", 1)[0]
    dc = state.attributes.get("device_class")
    return {
        "weather": domain == "weather",
        "grid_power": domain == "sensor" and dc == "power",
        "pv_power": domain == "sensor" and dc == "power",
        "grid_energy": domain == "sensor" and dc == "energy",
        "battery_soc": domain == "sensor" and dc == "battery",
        "vehicle_soc": domain == "sensor" and dc == "battery",
        "charge_mode": domain in ("select", "input_select"),
    }.get(key, False)


@websocket_api.websocket_command(
    {vol.Required("type"): "werner/energy", vol.Required("entry_id"): str}
)
@callback
def ws_energy(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Was die Energie-Anzeige zeigen könnte – und was gewählt ist."""
    entry = _entry(hass, msg["entry_id"])
    if entry is None or not (connection.user.is_admin or _is_own(hass, entry, connection.user.id)):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Das dürfen nur Sie selbst sehen.")
        return
    all_states = hass.states.async_all(["weather", "sensor", "select", "input_select"])
    candidates = {
        key: [
            {"entity_id": s.entity_id, "name": s.name}
            for s in sorted(all_states, key=lambda s: s.name.lower())
            if _energy_fits(hass, key, s.entity_id)
        ]
        for key in ENERGY_ENTITY_KEYS
    }
    current = {key: entry.options.get(key, "") for key in ENERGY_ENTITY_KEYS}
    current[CONF_PV_KWP] = entry.options.get(CONF_PV_KWP, 0)
    current[CONF_VEHICLE_NAME] = entry.options.get(CONF_VEHICLE_NAME, "")
    connection.send_result(msg["id"], {"current": current, "candidates": candidates})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "werner/resident/energy",
        vol.Required("entry_id"): str,
        vol.Required("values"): {
            vol.Optional(k): str for k in (*ENERGY_ENTITY_KEYS, CONF_VEHICLE_NAME)
        }
        | {vol.Optional(CONF_PV_KWP): vol.All(vol.Coerce(float), vol.Range(min=0, max=100))},
    }
)
@callback
def ws_set_energy(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Der Bewohner wählt selbst, was die Energie-Anzeige zeigt. Leer heißt: nicht zeigen."""
    entry = _entry(hass, msg["entry_id"])
    if entry is None or not (connection.user.is_admin or _is_own(hass, entry, connection.user.id)):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Das dürfen nur Sie selbst ändern.")
        return
    options = dict(entry.options)
    for key, value in msg["values"].items():
        if key in ENERGY_ENTITY_KEYS:
            value = value.strip()
            if value and value != entry.options.get(key) and not (
                connection.user.is_admin or _energy_fits(hass, key, value)
            ):
                connection.send_error(msg["id"], ERR_INVALID, f"{value} passt hier nicht.")
                return
            if value:
                options[key] = value
            else:
                options.pop(key, None)
        elif key == CONF_VEHICLE_NAME:
            options[key] = value.strip()[:40]
        else:
            options[key] = value
    hass.config_entries.async_update_entry(entry, options=options)
    connection.send_result(msg["id"], {})


# ------------------------------------------------------------------- Signal


def _has_resident(hass: HomeAssistant, user_id: str, is_admin: bool) -> bool:
    return is_admin or any(_is_own(hass, e, user_id) for e in _entries(hass))


@websocket_api.websocket_command({vol.Required("type"): "werner/signal/status"})
@websocket_api.async_response
async def ws_signal_status(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Ist die Signal-App da, und ist ein Konto verbunden? Die Nummer bleibt verborgen."""
    if not _has_resident(hass, connection.user.id, connection.user.is_admin):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Nur für Bewohner.")
        return
    client = get_client(hass)
    url = await client.async_url()
    if not url:
        connection.send_result(msg["id"], {"available": False, "connected": False, "text": "Die Signal-App ist nicht installiert."})
        return
    try:
        accounts = await client.async_accounts()
    except SignalError as err:
        connection.send_result(msg["id"], {"available": False, "connected": False, "text": str(err)})
        return
    connection.send_result(msg["id"], {"available": True, "connected": bool(accounts), "text": ""})


@websocket_api.websocket_command({vol.Required("type"): "werner/signal/qr"})
@websocket_api.async_response
async def ws_signal_qr(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """QR-Code zum Verbinden als Bild (base64)."""
    if not _has_resident(hass, connection.user.id, connection.user.is_admin):
        connection.send_error(msg["id"], ERR_NOT_ALLOWED, "Nur für Bewohner.")
        return
    try:
        png = await get_client(hass).async_qr()
    except SignalError as err:
        connection.send_error(msg["id"], ERR_INVALID, str(err))
        return
    import base64  # noqa: PLC0415

    connection.send_result(msg["id"], {"image": "data:image/png;base64," + base64.b64encode(png).decode()})
