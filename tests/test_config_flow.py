"""Einrichtungs-Assistent und Optionen."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.werner.const import DOMAIN

from .conftest import NOTIFY_ERIKA, PERSON


async def test_bewohner_anlegen(hass: HomeAssistant, notify_erika) -> None:
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


async def test_unbekannter_benachrichtigungsdienst(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"name": "Erika", "person": PERSON, "notify_service": "mobile_app_gibt_es_nicht"},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"notify_service": "notify_not_found"}


async def test_person_nur_einmal(hass: HomeAssistant) -> None:
    MockConfigEntry(domain=DOMAIN, unique_id=PERSON, data={}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Erika", "person": PERSON}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


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
