"""Hilfen für die Oberfläche: verständliche Gerätenamen und das Handy einer Person."""

from __future__ import annotations

import re

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

_PREFIX = re.compile(r"^\s*\[[^\]]*\]\s*")  # z. B. „[evcc] “
_QUOTES = re.compile(r"[\"'„“”‚‘’]")
_SPACES = re.compile(r"\s+")


def _tidy_word(word: str) -> str:
    """GOODWE → Goodwe, aber kurze Abkürzungen wie PV, WP oder ID.3 bleiben."""
    letters = re.sub(r"[^A-Za-zÄÖÜäöü]", "", word)
    if len(letters) > 3 and letters.isupper():
        return word.capitalize()
    return word


def clean_name(name: str) -> str:
    """Technische Namen lesbar machen: Präfixe, Anführungszeichen, Unterstriche."""
    text = _PREFIX.sub("", name or "")
    text = _QUOTES.sub("", text).replace("_", " ")
    text = _SPACES.sub(" ", text).strip()
    return " ".join(_tidy_word(w) for w in text.split(" ")) or (name or "")


def describe(hass: HomeAssistant, state: State) -> dict[str, str]:
    """Name und Raum einer Entität, so wie ein Bewohner sie verstehen kann."""
    name = clean_name(state.name)
    area = ""
    entry = er.async_get(hass).async_get(state.entity_id)
    if entry is not None:
        area_id = entry.area_id
        if area_id is None and entry.device_id:
            device = dr.async_get(hass).async_get(entry.device_id)
            area_id = device.area_id if device else None
        if area_id:
            found = ar.async_get(hass).async_get_area(area_id)
            area = found.name if found else ""
    return {"name": name, "area": area}


def suggest_notify(hass: HomeAssistant, person: str) -> str:
    """Das Handy (notify-Dienst der HA-App), das zu dieser Person gehört – oder leer."""
    state = hass.states.get(person)
    if state is None:
        return ""
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    for tracker in state.attributes.get("device_trackers") or []:
        entry = ent_reg.async_get(tracker)
        if entry is None or entry.platform != "mobile_app" or not entry.device_id:
            continue
        device = dev_reg.async_get(entry.device_id)
        if device is None:
            continue
        for label in (device.name_by_user, device.name):
            if label:
                service = f"mobile_app_{slugify(label)}"
                if hass.services.has_service("notify", service):
                    return service
    return ""
