"""Diagramme: Strompreis aus Nord Pool (Musterdaten)."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.util import dt as dt_util

from custom_components.werner.charts import async_charts
from custom_components.werner.const import CONF_PRICE_MARKUP, CONF_PRICE_VAT


def _nordpool(hass: HomeAssistant, eur_mwh: float) -> MockConfigEntry:
    """Nord Pool mit gleichem Preis in jeder Viertelstunde."""
    # Nicht wirklich laden: die Bibliothek von Nord Pool fehlt in der Testumgebung.
    np_entry = MockConfigEntry(domain="nordpool", title="Nord Pool")
    np_entry.add_to_hass(hass)

    async def _prices(call: ServiceCall) -> dict:
        day = dt_util.parse_date(call.data["date"])
        start = dt_util.as_utc(dt_util.start_of_local_day(day))
        rows = [
            {
                "start": (start + timedelta(minutes=15 * i)).isoformat(),
                "end": (start + timedelta(minutes=15 * (i + 1))).isoformat(),
                "price": eur_mwh,
            }
            for i in range(96)
        ]
        return {"GER": rows}

    hass.services.async_register(
        "nordpool", "get_prices_for_date", _prices, supports_response=SupportsResponse.ONLY
    )
    return np_entry


async def test_preis_je_stunde_mit_steuer_und_aufschlag(hass: HomeAssistant, entry) -> None:
    np_entry = _nordpool(hass, 200.0)  # 200 €/MWh = 20 ct/kWh
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_PRICE_VAT: True, CONF_PRICE_MARKUP: 10}
    )
    with patch(
        "custom_components.werner.charts._loaded",
        side_effect=lambda _hass, domain: [np_entry] if domain == "nordpool" else [],
    ):
        data = await async_charts(hass, entry)

    price = data["price"]
    assert price is not None
    # 20 ct × 1,19 + 10 ct Aufschlag
    assert {p["v"] for p in price["points"]} == {33.8}
    # Stündlich, 6 Stunden zurück bis 24 Stunden voraus (morgen gibt es hier immer Preise)
    assert len(price["points"]) == 30
    assert price["label"] == "Ihr Strompreis (geschätzt)"


async def test_ohne_quellen_keine_diagramme(hass: HomeAssistant, entry) -> None:
    entry.add_to_hass(hass)
    data = await async_charts(hass, entry)
    assert data["price"] is None and data["pv"] is None
