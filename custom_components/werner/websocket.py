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

from .const import (
    CONF_CONSENT,
    CONF_CREATED_BY,
    CONF_NAME,
    CONF_NOTIFY,
    CONF_PERSON,
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
