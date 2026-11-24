"""Selbstbestimmung: Bewohner richten Werner selbst ein, andere nur mit Zustimmung."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.werner.const import DOMAIN

from .conftest import NOTIFY_ERIKA, PERSON, run

KARL = "person.karl"


async def _haushalt(hass: HomeAssistant, user_id: str, other_user_id: str | None = None) -> None:
    """Erika gehört zum angemeldeten Benutzer, Karl zu einem anderen."""
    assert await async_setup_component(hass, "websocket_api", {})
    hass.states.async_set(PERSON, "home", {"user_id": user_id, "friendly_name": "Erika Muster"})
    hass.states.async_set(KARL, "home", {"user_id": other_user_id, "friendly_name": "Karl Muster"})
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()


async def test_selbst_einschalten(hass: HomeAssistant, hass_read_only_user, hass_read_only_access_token, hass_ws_client, notify_erika) -> None:
    await _haushalt(hass, hass_read_only_user.id)
    ws = await hass_ws_client(hass, hass_read_only_access_token)

    await ws.send_json_auto_id({"type": "werner/resident/add", "person": PERSON, "name": "Erika", "notify": NOTIFY_ERIKA})
    res = await ws.receive_json()
    assert res["success"], res
    assert res["result"]["consent"] is True
    await run(hass)

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.runtime_data.consent is True

    await ws.send_json_auto_id({"type": "werner/household"})
    res = await ws.receive_json()
    mine = res["result"]["residents"][0]
    assert mine["mine"] and mine["notify"] == NOTIFY_ERIKA


async def test_andere_nur_mit_zustimmung(hass: HomeAssistant, hass_admin_user, hass_read_only_user, hass_read_only_access_token, hass_ws_client) -> None:
    # Erika (nicht Admin) trägt Karl ein; Karl gehört dem Admin-Benutzer.
    await _haushalt(hass, hass_read_only_user.id, hass_admin_user.id)
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "werner/resident/add", "person": KARL, "name": "Karl"})
    res = await ws.receive_json()
    assert res["success"], res
    assert res["result"]["consent"] is False
    await run(hass)

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    bewohner = entry.runtime_data
    assert bewohner.consent is False
    assert not bewohner._may_ask()

    # Erika sieht nur den Namen, nicht Karls Einstellungen.
    await ws.send_json_auto_id({"type": "werner/household"})
    res = await ws.receive_json()
    karl = res["result"]["residents"][0]
    assert "notify" not in karl and "person" not in karl
    assert karl["may_remove"] is True  # noch nicht bestätigt: zurücknehmen erlaubt

    # Erika kann nicht für Karl zustimmen.
    await ws.send_json_auto_id({"type": "werner/resident/consent", "entry_id": entry.entry_id, "accept": True})
    res = await ws.receive_json()
    assert not res["success"]

    # Karl stimmt selbst zu.
    admin_ws = await hass_ws_client(hass)
    await admin_ws.send_json_auto_id({"type": "werner/resident/consent", "entry_id": entry.entry_id, "accept": True})
    res = await admin_ws.receive_json()
    assert res["success"], res
    await run(hass)
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.runtime_data.consent is True

    # Nach der Zustimmung kann Erika Karl nicht mehr entfernen.
    await ws.send_json_auto_id({"type": "werner/resident/remove", "entry_id": entry.entry_id})
    res = await ws.receive_json()
    assert not res["success"]


async def test_ablehnen_loescht(hass: HomeAssistant, hass_admin_user, hass_read_only_user, hass_read_only_access_token, hass_ws_client) -> None:
    await _haushalt(hass, hass_read_only_user.id, hass_admin_user.id)
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "werner/resident/add", "person": KARL, "name": "Karl"})
    assert (await ws.receive_json())["success"]
    await run(hass)
    entry_id = hass.config_entries.async_entries(DOMAIN)[0].entry_id

    admin_ws = await hass_ws_client(hass)
    await admin_ws.send_json_auto_id({"type": "werner/resident/consent", "entry_id": entry_id, "accept": False})
    assert (await admin_ws.receive_json())["success"]
    await run(hass)
    assert hass.config_entries.async_entries(DOMAIN) == []


async def test_fremde_einstellungen_gesperrt(hass: HomeAssistant, hass_admin_user, hass_read_only_user, hass_read_only_access_token, hass_ws_client, entry: MockConfigEntry) -> None:
    # Erika gehört hier dem Admin; der andere Benutzer darf sie nicht ändern oder entfernen.
    await _haushalt(hass, hass_admin_user.id)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "werner/resident/update", "entry_id": entry.entry_id, "name": "X"})
    assert not (await ws.receive_json())["success"]
    await ws.send_json_auto_id({"type": "werner/resident/remove", "entry_id": entry.entry_id})
    assert not (await ws.receive_json())["success"]

    # Ohne eigene Anmeldung kann niemand außer dem Helfer eingetragen werden.
    hass.states.async_set("person.gast", "home", {"friendly_name": "Gast"})
    await ws.send_json_auto_id({"type": "werner/resident/add", "person": "person.gast", "name": "Gast"})
    assert not (await ws.receive_json())["success"]


async def test_selbst_beenden(hass: HomeAssistant, hass_read_only_user, hass_read_only_access_token, hass_ws_client, notify_erika) -> None:
    await _haushalt(hass, hass_read_only_user.id)
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "werner/resident/add", "person": PERSON, "name": "Erika"})
    assert (await ws.receive_json())["success"]
    await run(hass)
    entry_id = hass.config_entries.async_entries(DOMAIN)[0].entry_id

    await ws.send_json_auto_id({"type": "werner/resident/update", "entry_id": entry_id, "name": "Erika M.", "notify": NOTIFY_ERIKA})
    assert (await ws.receive_json())["success"]
    await run(hass)
    entry = hass.config_entries.async_get_entry(entry_id)
    assert entry.title == "Erika M." and entry.data["notify_service"] == NOTIFY_ERIKA

    await ws.send_json_auto_id({"type": "werner/resident/remove", "entry_id": entry_id})
    assert (await ws.receive_json())["success"]
    await run(hass)
    assert hass.config_entries.async_entries(DOMAIN) == []


async def test_quellen_selbst_waehlen(hass: HomeAssistant, hass_admin_user, hass_read_only_user, hass_read_only_access_token, hass_ws_client, notify_erika) -> None:
    await _haushalt(hass, hass_read_only_user.id)
    hass.states.async_set("sensor.hausleistung", "250", {"device_class": "power", "unit_of_measurement": "W"})
    hass.states.async_set("binary_sensor.flur", "off", {"device_class": "motion"})
    hass.states.async_set("sensor.temperatur", "21", {"device_class": "temperature"})
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "werner/resident/add", "person": PERSON, "name": "Erika"})
    assert (await ws.receive_json())["success"]
    await run(hass)
    entry = hass.config_entries.async_entries(DOMAIN)[0]

    await ws.send_json_auto_id({"type": "werner/sources", "entry_id": entry.entry_id})
    res = await ws.receive_json()
    ids = {c["entity_id"] for c in res["result"]["candidates"]}
    assert {"sensor.hausleistung", "binary_sensor.flur"} <= ids
    assert "sensor.temperatur" not in ids
    assert not any(i.startswith(("sensor.werner", "switch.werner")) for i in ids)

    await ws.send_json_auto_id({"type": "werner/resident/sources", "entry_id": entry.entry_id,
                                "sources": ["sensor.hausleistung", "binary_sensor.flur"], "baseload_w": 200})
    assert (await ws.receive_json())["success"]
    await run(hass)
    assert entry.runtime_data.sources == ["sensor.hausleistung", "binary_sensor.flur"]
    assert entry.runtime_data.baseload == 200

    # Unpassende Entitäten lehnt Werner ab.
    await ws.send_json_auto_id({"type": "werner/resident/sources", "entry_id": entry.entry_id, "sources": ["sensor.temperatur"]})
    assert not (await ws.receive_json())["success"]

    # Ein anderer Benutzer darf Erikas Quellen nicht ändern.
    other = await hass_ws_client(hass)  # Admin: darf als Helfer
    await other.send_json_auto_id({"type": "werner/sources", "entry_id": entry.entry_id})
    assert (await other.receive_json())["success"]


async def test_energie_anzeige_selbst_waehlen(hass: HomeAssistant, hass_read_only_user, hass_read_only_access_token, hass_ws_client, notify_erika) -> None:
    await _haushalt(hass, hass_read_only_user.id)
    hass.states.async_set("weather.zuhause", "sunny", {})
    hass.states.async_set("sensor.netz", "300", {"device_class": "power", "unit_of_measurement": "W"})
    hass.states.async_set("sensor.zaehler", "1234", {"device_class": "energy", "unit_of_measurement": "kWh"})
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "werner/resident/add", "person": PERSON, "name": "Erika"})
    assert (await ws.receive_json())["success"]
    await run(hass)
    entry = hass.config_entries.async_entries(DOMAIN)[0]

    await ws.send_json_auto_id({"type": "werner/energy", "entry_id": entry.entry_id})
    res = (await ws.receive_json())["result"]
    assert {c["entity_id"] for c in res["candidates"]["weather"]} == {"weather.zuhause"}
    assert "sensor.zaehler" in {c["entity_id"] for c in res["candidates"]["grid_energy"]}
    assert "sensor.zaehler" not in {c["entity_id"] for c in res["candidates"]["grid_power"]}

    await ws.send_json_auto_id({"type": "werner/resident/energy", "entry_id": entry.entry_id,
                                "values": {"weather": "weather.zuhause", "grid_power": "sensor.netz", "pv_kwp": 1.5}})
    assert (await ws.receive_json())["success"]
    await run(hass)
    assert entry.options["grid_power"] == "sensor.netz" and entry.options["pv_kwp"] == 1.5

    # Unpassend: ein Energiezähler als Leistung
    await ws.send_json_auto_id({"type": "werner/resident/energy", "entry_id": entry.entry_id, "values": {"grid_power": "sensor.zaehler"}})
    assert not (await ws.receive_json())["success"]

    # Leer blendet aus
    await ws.send_json_auto_id({"type": "werner/resident/energy", "entry_id": entry.entry_id, "values": {"grid_power": ""}})
    assert (await ws.receive_json())["success"]
    await run(hass)
    assert "grid_power" not in entry.options
