"""Solaranlage für die Sonnen-Vorhersage selbst einrichten (aus „Werner einstellen“).

Der Bewohner nennt nur drei Dinge in einfachen Worten: Leistung, Himmelsrichtung
und Neigung. Werner legt dafür einen Eintrag der eingebauten Integration
„Forecast.Solar“ am Standort des Zuhauses an. Ändert der Bewohner die Angaben,
ersetzt Werner nur den Eintrag, den er selbst angelegt hat – fremde Einträge
bleiben unberührt.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import SOURCE_USER, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .const import CONF_PV_FORECAST, CONF_PV_KWP, CONF_PV_OWN

_LOGGER = logging.getLogger(__name__)

DOMAIN_FS = "forecast_solar"


TITLE = "Solaranlage (Werner)"


class SolarError(Exception):
    """Einrichtung hat nicht geklappt – Text ist für den Bewohner gedacht."""


def _pick_field(schema: list[dict[str, Any]] | None, *words: str) -> str | None:
    for field in schema or []:
        name = str(field.get("name", ""))
        if all(w in name for w in words) and "sensor" not in name:
            return name
    return None


def _schema_list(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Feldnamen eines Flow-Schritts."""
    schema = result.get("data_schema")
    keys = getattr(schema, "schema", None) or {}
    return [{"name": str(getattr(k, "schema", k))} for k in keys]


def _own_entry(hass: HomeAssistant, entry: ConfigEntry) -> ConfigEntry | None:
    """Der von Werner angelegte Forecast.Solar-Eintrag.

    Fehlt die Zuordnung (z. B. nach einer Neueinrichtung des Bewohners), gilt die
    eindeutige „Solaranlage (Werner)“ als eigene Anlage.
    """
    own = entry.options.get(CONF_PV_OWN)
    fs = hass.config_entries.async_get_entry(own) if own else None
    if fs is None:
        mine = [e for e in hass.config_entries.async_entries(DOMAIN_FS) if e.title == TITLE]
        fs = mine[0] if len(mine) == 1 else None
    return fs


async def async_set_plane(
    hass: HomeAssistant,
    entry: ConfigEntry,
    watt_peak: int,
    azimuth: int,
    declination: int,
) -> str:
    """Eigenen Forecast.Solar-Eintrag anlegen oder ersetzen. Ergebnis: entry_id."""
    if not hass.config.latitude and not hass.config.longitude:
        raise SolarError("Für die Vorhersage braucht Home Assistant den Standort des Zuhauses.")
    await async_remove_plane(hass, entry, keep_option=True)

    flow = hass.config_entries.flow
    result = await flow.async_init(DOMAIN_FS, context={"source": SOURCE_USER})
    try:
        for _ in range(4):
            if result["type"] is FlowResultType.CREATE_ENTRY:
                break
            if result["type"] is FlowResultType.ABORT:
                raise SolarError(f"Forecast.Solar lehnt ab: {result.get('reason')}")
            fields = _schema_list(result)
            names = {f.get("name") for f in fields}
            answer: dict[str, Any] = {}
            if "location" in names:
                answer = {"location": "home", "declination_source": "fixed", "azimuth_source": "fixed"}
                answer = {k: v for k, v in answer.items() if k in names}
            else:
                if key := _pick_field(fields, "declination"):
                    answer[key] = declination
                if key := _pick_field(fields, "azimuth"):
                    answer[key] = azimuth
                if key := _pick_field(fields, "power"):
                    answer[key] = watt_peak
                if "name" in names:
                    answer["name"] = TITLE
            if not answer:
                raise SolarError("Forecast.Solar fragt etwas, das Werner nicht kennt.")
            result = await flow.async_configure(result["flow_id"], answer)
            if result.get("errors"):
                raise SolarError(f"Forecast.Solar meldet: {', '.join(result['errors'].values())}")
    except SolarError:
        if result.get("flow_id") and result["type"] is not FlowResultType.CREATE_ENTRY:
            flow.async_abort(result["flow_id"])
        raise
    if result["type"] is not FlowResultType.CREATE_ENTRY:
        flow.async_abort(result["flow_id"])
        raise SolarError("Die Einrichtung von Forecast.Solar ist nicht fertig geworden.")

    new_entry: ConfigEntry = result["result"]
    if new_entry.title != TITLE:
        hass.config_entries.async_update_entry(new_entry, title=TITLE)
    options = dict(entry.options)
    options[CONF_PV_FORECAST] = new_entry.entry_id
    options[CONF_PV_OWN] = new_entry.entry_id
    options[CONF_PV_KWP] = round(watt_peak / 1000, 2)
    hass.config_entries.async_update_entry(entry, options=options)
    return new_entry.entry_id


async def async_remove_plane(hass: HomeAssistant, entry: ConfigEntry, keep_option: bool = False) -> None:
    """Den von Werner angelegten Forecast.Solar-Eintrag entfernen."""
    fs = _own_entry(hass, entry)
    own = fs.entry_id if fs else None
    if fs is not None:
        await hass.config_entries.async_remove(fs.entry_id)
    if keep_option:
        return
    options = dict(entry.options)
    for key in (CONF_PV_OWN,):
        options.pop(key, None)
    if options.get(CONF_PV_FORECAST) == own:
        options.pop(CONF_PV_FORECAST, None)
    hass.config_entries.async_update_entry(entry, options=options)


def plane_of(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any] | None:
    """Angaben der eigenen Anlage (für die Anzeige), soweit lesbar."""
    fs = _own_entry(hass, entry)
    if fs is None:
        return None
    values: dict[str, Any] = {**fs.data, **fs.options}
    for sub in getattr(fs, "subentries", {}).values():
        values.update(sub.data)
        break
    def num(*words: str) -> Any:
        for k, v in values.items():
            if all(w in k for w in words) and "sensor" not in k:
                return v
        return None
    return {
        "entry_id": fs.entry_id,
        "watt_peak": num("power"),
        "azimuth": num("azimuth"),
        "declination": num("declination"),
    }
