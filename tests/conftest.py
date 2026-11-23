"""Gemeinsame Test-Hilfen für Werner (Musterdaten: Erika, Sabine)."""

from __future__ import annotations

import asyncio

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from homeassistant.core import HomeAssistant, ServiceCall

from custom_components.werner.const import DOMAIN

PERSON = "person.erika"
NOTIFY_ERIKA = "mobile_app_erikas_handy"
NOTIFY_SABINE = "mobile_app_sabines_handy"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Eigene Integrationen in allen Tests erlauben."""
    yield


@pytest.fixture
def notify_erika(hass: HomeAssistant) -> list[ServiceCall]:
    """Handy des Bewohners."""
    return async_mock_service(hass, "notify", NOTIFY_ERIKA)


@pytest.fixture
def notify_sabine(hass: HomeAssistant) -> list[ServiceCall]:
    """Handy der ersten Vertrauensperson."""
    return async_mock_service(hass, "notify", NOTIFY_SABINE)


@pytest.fixture
def entry() -> MockConfigEntry:
    """Bewohnerin Erika mit Stromzähler als Aktivitätsquelle."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Erika",
        unique_id=PERSON,
        data={"name": "Erika", "person": PERSON, "notify_service": NOTIFY_ERIKA},
        options={"activity_sources": ["sensor.hausleistung"], "baseload_w": 300},
    )


async def run(hass: HomeAssistant) -> None:
    """Hintergrund-Abläufe ein paar Schritte laufen lassen."""
    for _ in range(5):
        await hass.async_block_till_done()
        await asyncio.sleep(0)
