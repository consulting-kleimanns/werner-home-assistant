"""Signal: Vertrauensperson per Signal informieren, Antworten 1/2/3 auswerten."""

from __future__ import annotations

from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.werner import bewohner as bewohner_mod
from custom_components.werner.const import STATUS_INFORMED, STATUS_OK
from custom_components.werner.signal_messenger import SignalError, normalize_number

from .test_ablauf import _setup
from .conftest import run


class FakeSignal:
    """Ersetzt die Signal-App im Test."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []
        self.listeners: list = []
        self.fail = False

    async def async_send(self, recipient: str, message: str) -> None:
        if self.fail:
            raise SignalError("Signal ist noch nicht mit Werner verbunden.")
        self.sent.append((normalize_number(recipient), message))

    def async_listen(self, cb):
        self.listeners.append(cb)
        return lambda: self.listeners.remove(cb)

    def reply(self, source: str, text: str) -> None:
        for cb in list(self.listeners):
            cb(normalize_number(source), text)


@pytest.fixture
def fake_signal(monkeypatch) -> FakeSignal:
    fake = FakeSignal()
    monkeypatch.setattr(bewohner_mod, "get_client", lambda hass: fake)
    return fake


def _sabine_signal(bewohner) -> None:
    bewohner.set_setting("person_1_name", "Sabine")
    bewohner.set_setting("person_1_way", "signal")
    bewohner.set_setting("person_1_phone", "0170 0000000")


def test_nummer_normalisieren() -> None:
    assert normalize_number("0170 0000000") == "+491700000000"
    assert normalize_number("+49 (170) 000-0000") == "+491700000000"
    assert normalize_number("0049 170 0000000") == "+491700000000"


async def test_signal_ich_kuemmere_mich(hass: HomeAssistant, entry, notify_erika, fake_signal) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_signal(bewohner)
    bewohner.ask("Test-Nachfrage.")
    await run(hass)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=11))
    await run(hass)

    assert bewohner.status == STATUS_INFORMED
    assert len(fake_signal.sent) == 1
    number, text = fake_signal.sent[0]
    assert number == "+491700000000"
    assert "Erika" in text and "1 = Ich kümmere mich" in text

    # Eine Antwort von einer fremden Nummer zählt nicht.
    fake_signal.reply("+49 151 1111111", "1")
    await run(hass)
    assert bewohner.procedure is not None

    fake_signal.reply("+49 170 0000000", "1")
    await run(hass)
    assert bewohner.procedure is None
    assert "Sabine" in notify_erika[-1].data["message"]
    assert "Danke" in fake_signal.sent[-1][1]


async def test_signal_fehlalarm(hass: HomeAssistant, entry, notify_erika, fake_signal) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_signal(bewohner)
    bewohner.help()
    await run(hass)
    fake_signal.reply("01700000000", "2 Fehlalarm")
    await run(hass)
    assert bewohner.status == STATUS_OK
    assert bewohner.procedure is None


async def test_signal_nicht_verbunden(hass: HomeAssistant, entry, notify_erika, fake_signal) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_signal(bewohner)
    fake_signal.fail = True
    bewohner.help()
    await run(hass)
    # Werner gibt nicht auf, sondern sagt dem Bewohner, dass niemand erreicht wurde.
    assert bewohner.procedure is None
    assert "112" in notify_erika[-1].data["message"]


async def test_signal_test_nachricht(hass: HomeAssistant, entry, notify_erika, fake_signal) -> None:
    bewohner = await _setup(hass, entry)
    _sabine_signal(bewohner)
    res = await bewohner.async_test_person(1)
    assert res["ok"] is True
    assert "Test" in fake_signal.sent[0][1]
