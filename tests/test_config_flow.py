"""Einrichtungs-Assistent und Optionen."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.werner.const import DOMAIN
from custom_components.werner.geraete import clean_name, suggest_notify

from .conftest import NOTIFY_ERIKA, PERSON


def _erika(hass: HomeAssistant, trackers: list[str] | None = None) -> None:
    hass.states.async_set(
        PERSON, "home", {"friendly_name": "Erika Muster", "device_trackers": trackers or []}
    )


def _handy(hass: HomeAssistant) -> str:
    """Erikas Handy mit der HA-App: Gerät „Erikas Handy“ und dessen Tracker."""
    entry = MockConfigEntry(domain="mobile_app")
    entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={("mobile_app", "erika")}, name="Erikas Handy"
    )
    tracker = er.async_get(hass).async_get_or_create(
        "device_tracker", "mobile_app", "erika", device_id=device.id, config_entry=entry
    )
    return tracker.entity_id


async def test_bewohner_anlegen(hass: HomeAssistant, notify_erika) -> None:
    _erika(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"name": " Erika ", "person": PERSON, "notify_service": f"notify.{NOTIFY_ERIKA}"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Erika"
    assert result["data"] == {
        "name": "Erika",
        "person": PERSON,
        "notify_service": NOTIFY_ERIKA,
    }


async def test_nur_person_waehlen(hass: HomeAssistant, notify_erika) -> None:
    """Name und Handy findet Werner selbst."""
    _erika(hass, [_handy(hass)])
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"person": PERSON})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {"name": "Erika", "person": PERSON, "notify_service": NOTIFY_ERIKA}


async def test_unbekannter_benachrichtigungsdienst(hass: HomeAssistant) -> None:
    _erika(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"name": "Erika", "person": PERSON, "notify_service": "mobile_app_gibt_es_nicht"},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"notify_service": "notify_not_found"}


async def test_ohne_person(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_person"


async def test_person_nur_einmal(hass: HomeAssistant) -> None:
    _erika(hass)
    MockConfigEntry(domain=DOMAIN, unique_id=PERSON, data={}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "all_persons_configured"


def test_namen_lesbar() -> None:
    assert clean_name("[evcc] 'GOODWE_BATTERY' Leistung") == "Goodwe Battery Leistung"
    assert clean_name("PV Leistung") == "PV Leistung"
    assert clean_name("Bewegungsmelder Flur") == "Bewegungsmelder Flur"


async def test_handy_vorschlag(hass: HomeAssistant, notify_erika) -> None:
    _erika(hass, ["device_tracker.fremd", _handy(hass)])
    assert suggest_notify(hass, PERSON) == NOTIFY_ERIKA
    assert suggest_notify(hass, "person.gibt_es_nicht") == ""


async def test_optionen(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    hass.states.async_set(PERSON, "home")
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"activity_sources": ["sensor.hausleistung", "binary_sensor.flur"], "baseload_w": 250},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["baseload_w"] == 250
    assert entry.runtime_data.sources == ["sensor.hausleistung", "binary_sensor.flur"]
