"""E-Mail: Einstellungen nur für Helfer, Versand, Antwort per Klick."""

from __future__ import annotations

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.core_config import async_process_ha_core_config
from homeassistant.setup import async_setup_component

from custom_components.werner import mail as mail_mod
from custom_components.werner.const import STATUS_OK
from custom_components.werner.mail import get_mail

from .conftest import run
from .test_ablauf import _setup

POSTFACH = {
    "server": "smtp.example.org",
    "port": 587,
    "security": "starttls",
    "user": "werner@example.org",
    "password": "geheim",
    "sender_name": "Werner",
}


@pytest.fixture
def sent(monkeypatch) -> list[dict]:
    """Versand abfangen statt wirklich zu senden."""
    out: list[dict] = []

    def _send(settings, to, subject, text, html_body):
        out.append({"settings": settings, "to": to, "subject": subject, "text": text, "html": html_body})

    monkeypatch.setattr(mail_mod.WernerMail, "_send", staticmethod(_send))
    return out


def _sabine_mail(bewohner) -> None:
    bewohner.set_setting("person_1_name", "Sabine")
    bewohner.set_setting("person_1_way", "e_mail")
    bewohner.set_setting("person_1_e_mail", "sabine@example.org")


async def test_nicht_eingerichtet(hass: HomeAssistant, entry, notify_erika, sent) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_mail(bewohner)
    res = await bewohner.async_test_person(1)
    assert res["ok"] is False
    assert "Helfer" in res["text"]
    assert not sent


async def test_test_mail(hass: HomeAssistant, entry, notify_erika, sent) -> None:
    bewohner = await _setup(hass, entry)
    await get_mail(hass).async_save(POSTFACH)
    _sabine_mail(bewohner)
    res = await bewohner.async_test_person(1)
    assert res["ok"] is True
    assert sent[0]["to"] == "sabine@example.org"
    assert "Erika" in sent[0]["text"]


async def test_passwort_bleibt(hass: HomeAssistant, sent) -> None:
    mail = get_mail(hass)
    await mail.async_save(POSTFACH)
    await mail.async_save({**POSTFACH, "password": "", "server": "smtp2.example.org"})
    assert mail.settings["password"] == "geheim"
    assert mail.public()["server"] == "smtp2.example.org"
    assert "password" not in mail.public()


async def test_alarm_per_mail_mit_antwort(hass: HomeAssistant, entry, notify_erika, sent, hass_client_no_auth) -> None:
    await async_process_ha_core_config(hass, {"external_url": "https://werner.example.org"})
    assert await async_setup_component(hass, "webhook", {})
    bewohner = await _setup(hass, entry)
    await get_mail(hass).async_save(POSTFACH)
    _sabine_mail(bewohner)
    bewohner.help()
    await run(hass)

    assert len(sent) == 1
    text = sent[0]["text"]
    assert "Sabine" in text and "112" in text
    link = next(line.split(": ", 1)[1] for line in text.splitlines() if line.startswith("Fehlalarm: "))
    path = link.removeprefix("https://werner.example.org")

    client = await hass_client_no_auth()
    # Ein bloßes Öffnen (z. B. durch einen Virenscanner) zählt nicht.
    resp = await client.get(path)
    assert resp.status == 200
    await run(hass)
    assert bewohner.procedure is not None

    resp = await client.post(path)
    assert resp.status == 200
    await run(hass)
    assert bewohner.status == STATUS_OK
    assert bewohner.procedure is None


async def test_nur_helfer_aendern(hass: HomeAssistant, hass_read_only_access_token, hass_ws_client) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    assert await async_setup_component(hass, "werner", {})
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "werner/mail/set", **POSTFACH})
    res = await ws.receive_json()
    assert not res["success"]
    await ws.send_json_auto_id({"type": "werner/mail/status"})
    res = await ws.receive_json()
    assert res["result"] == {"configured": False, "may_edit": False}
