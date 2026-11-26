"""Werners Ablauf: Aktivität, Nachfrage, Eskalation, Pause, Hilfe."""

from __future__ import annotations

from datetime import timedelta

from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.werner.const import (
    DOMAIN,
    STATUS_ASKING,
    STATUS_HELP,
    STATUS_INFORMED,
    STATUS_OK,
    STATUS_PAUSED,
)

from .conftest import NOTIFY_SABINE, PERSON, run


async def _setup(hass: HomeAssistant, entry: MockConfigEntry):
    hass.states.async_set(PERSON, "home")
    hass.states.async_set("sensor.hausleistung", "120")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry.runtime_data


def _sabine_eintragen(bewohner) -> None:
    bewohner.set_setting("person_1_name", "Sabine")
    bewohner.set_setting("person_1_way", "ha_app")
    bewohner.set_setting("person_1_contact", NOTIFY_SABINE)


def _action(call, index: int) -> str:
    return call.data["data"]["actions"][index]["action"]


async def test_entitaeten_angelegt(hass: HomeAssistant, entry, notify_erika) -> None:
    await _setup(hass, entry)
    states = hass.states.async_all()
    werner = [s for s in states if s.entity_id.split(".")[0] in (
        "sensor", "switch", "number", "text", "select", "button") and s.entity_id != "sensor.hausleistung"]
    # 2 Sensoren, 6 Schalter, 3 Zahlen, 12 Texte, 3 Auswahlen, 2 Knöpfe
    assert len(werner) == 29
    status = [s for s in werner if s.attributes.get("device_class") == "enum"]
    assert status and status[0].state == STATUS_OK


async def test_grundlast(hass: HomeAssistant, entry, notify_erika) -> None:
    bewohner = await _setup(hass, entry)
    assert bewohner.last_activity is None

    hass.states.async_set("sensor.hausleistung", "180")  # unter Grundlast
    await hass.async_block_till_done()
    assert bewohner.last_activity is None

    hass.states.async_set("sensor.hausleistung", "1900")  # Wasserkocher
    await hass.async_block_till_done()
    assert bewohner.last_activity is not None


async def test_nachfrage_alles_gut(hass: HomeAssistant, entry, notify_erika) -> None:
    bewohner = await _setup(hass, entry)
    bewohner.ask("Test-Nachfrage.")
    await run(hass)

    assert bewohner.status == STATUS_ASKING
    assert len(notify_erika) == 1
    hass.bus.async_fire("mobile_app_notification_action", {"action": _action(notify_erika[0], 0)})
    await run(hass)

    assert bewohner.status == STATUS_OK
    assert bewohner.procedure is None
    assert bewohner.last_activity is not None


async def test_ohne_antwort_vertrauensperson(
    hass: HomeAssistant, entry, notify_erika, notify_sabine
) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_eintragen(bewohner)
    bewohner.ask("Test-Nachfrage.")
    await run(hass)
    assert not notify_sabine

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=11))
    await run(hass)

    assert bewohner.status == STATUS_INFORMED
    assert len(notify_sabine) == 1
    assert "Erika" in notify_sabine[0].data["title"]

    # Sabine: 1 · Ich kümmere mich
    hass.bus.async_fire("mobile_app_notification_action", {"action": _action(notify_sabine[0], 0)})
    await run(hass)
    assert bewohner.procedure is None
    assert bewohner.status == STATUS_INFORMED
    assert "Sabine" in notify_erika[-1].data["message"]


async def test_fehlalarm(hass: HomeAssistant, entry, notify_erika, notify_sabine) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_eintragen(bewohner)
    bewohner.help()
    await run(hass)

    assert bewohner.status == STATUS_HELP
    assert len(notify_sabine) == 1
    assert "braucht Hilfe" in notify_sabine[0].data["title"]

    hass.bus.async_fire("mobile_app_notification_action", {"action": _action(notify_sabine[0], 1)})
    await run(hass)
    assert bewohner.status == STATUS_OK


async def test_niemand_erreicht(hass: HomeAssistant, entry, notify_erika, notify_sabine) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_eintragen(bewohner)
    bewohner.help()
    await run(hass)

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=16))
    await run(hass)

    assert bewohner.procedure is None
    assert "112" in notify_erika[-1].data["message"]


async def test_pause(hass: HomeAssistant, entry, notify_erika) -> None:
    bewohner = await _setup(hass, entry)
    bewohner.ask("Test-Nachfrage.")
    await run(hass)
    assert bewohner.status == STATUS_ASKING

    bewohner.set_setting("paused", True)
    await run(hass)
    assert bewohner.status == STATUS_PAUSED
    assert not bewohner.busy

    bewohner.ask("Darf nicht fragen.")
    await run(hass)
    assert bewohner.status == STATUS_PAUSED

    bewohner.set_setting("paused", False)
    await run(hass)
    assert bewohner.status == STATUS_OK


async def test_knopf_alles_gut_beendet_nachfrage(hass: HomeAssistant, entry, notify_erika) -> None:
    bewohner = await _setup(hass, entry)
    bewohner.ask("Test-Nachfrage.")
    await run(hass)

    button = er.async_get(hass).async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_all_good")
    assert button
    await hass.services.async_call("button", "press", {"entity_id": button}, blocking=True)
    await run(hass)
    assert bewohner.status == STATUS_OK
    assert not bewohner.busy


async def test_attribute_fuer_oberflaeche(hass: HomeAssistant, entry, notify_erika) -> None:
    await _setup(hass, entry)
    status_id = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_status")
    attrs = hass.states.get(status_id).attributes
    assert attrs["resident"] == "Erika"
    assert attrs["entry_id"] == entry.entry_id
    assert attrs["person"] == PERSON
    assert attrs["sources"] == ["sensor.hausleistung"]
    # Alle 29 Entitäten sind für die Oberfläche auffindbar.
    assert len(attrs["entities"]) == 29
    assert attrs["entities"]["status"] == status_id
    assert attrs["entities"]["person_2_way"].startswith("select.")


async def test_dienst_test_person(hass: HomeAssistant, entry, notify_erika, notify_sabine) -> None:
    bewohner = await _setup(hass, entry)
    response = await hass.services.async_call(
        DOMAIN, "test_person", {"config_entry_id": entry.entry_id, "person": 1},
        blocking=True, return_response=True,
    )
    assert response["ok"] is False  # noch niemand eingetragen

    _sabine_eintragen(bewohner)
    response = await hass.services.async_call(
        DOMAIN, "test_person", {"config_entry_id": entry.entry_id, "person": 1},
        blocking=True, return_response=True,
    )
    assert response["ok"] is True
    assert len(notify_sabine) == 1
    assert "Test" in notify_sabine[0].data["title"]


async def test_dienst_nachfragen(hass: HomeAssistant, entry, notify_erika) -> None:
    bewohner = await _setup(hass, entry)
    await hass.services.async_call(
        DOMAIN, "ask", {"config_entry_id": entry.entry_id, "reason": "Probe."}, blocking=True
    )
    await run(hass)
    assert bewohner.status == STATUS_ASKING
    assert "Probe." in notify_erika[0].data["message"]


async def test_aktivitaet_im_protokoll(hass: HomeAssistant, entry, notify_erika) -> None:
    bewohner = await _setup(hass, entry)
    logged = []
    bewohner.log = logged.append  # type: ignore[method-assign]
    hass.states.async_set("sensor.hausleistung", "2000")
    await hass.async_block_till_done()
    hass.states.async_set("sensor.hausleistung", "100")
    hass.states.async_set("sensor.hausleistung", "2100")
    await hass.async_block_till_done()
    # Höchstens ein Eintrag je Quelle in 30 Minuten
    assert len([m for m in logged if m.startswith("Aktivität bemerkt")]) == 1
