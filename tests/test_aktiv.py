"""Werner ist eine Option: neue Einrichtungen starten ausgeschaltet (Musterdaten: Erika)."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant

from custom_components.werner.const import DOMAIN, STATUS_OFF, STATUS_OK

from .conftest import NOTIFY_ERIKA, PERSON, run


async def _setup(hass: HomeAssistant, start_active: bool | None):
    data = {"name": "Erika", "person": PERSON, "notify_service": NOTIFY_ERIKA}
    if start_active is not None:
        data["start_active"] = start_active
    entry = MockConfigEntry(
        domain=DOMAIN, title="Erika", unique_id=PERSON, data=data,
        options={"activity_sources": ["sensor.hausleistung"], "baseload_w": 300},
    )
    hass.states.async_set(PERSON, "home")
    hass.states.async_set("sensor.hausleistung", "120")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry.runtime_data


async def test_neu_eingerichtet_ist_werner_aus(hass: HomeAssistant, notify_erika) -> None:
    bewohner = await _setup(hass, False)
    assert bewohner.settings["active"] is False
    assert bewohner.status == STATUS_OFF

    # Ausgeschaltet fragt Werner nicht nach und holt keine Hilfe.
    bewohner.ask("Test-Nachfrage.")
    bewohner.help()
    await run(hass)
    assert notify_erika == []
    assert bewohner.status == STATUS_OFF


async def test_bewusst_einschalten(hass: HomeAssistant, notify_erika) -> None:
    bewohner = await _setup(hass, False)
    switch = bewohner.entity_ids["active"]
    await hass.services.async_call("switch", "turn_on", {"entity_id": switch}, blocking=True)
    await run(hass)
    assert bewohner.settings["active"] is True
    assert bewohner.status == STATUS_OK

    await hass.services.async_call("switch", "turn_off", {"entity_id": switch}, blocking=True)
    await run(hass)
    assert bewohner.status == STATUS_OFF


async def test_bestehende_einrichtung_bleibt_eingeschaltet(hass: HomeAssistant) -> None:
    bewohner = await _setup(hass, None)
    assert bewohner.settings["active"] is True
    assert bewohner.status == STATUS_OK
