"""Werner – ein freundlicher Aufpasser für Senioren.

Jeder Bewohner ist ein eigener Konfigurationseintrag mit eigenem Gerät,
eigenen Einstellungen und eigenem Ablauf.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .bewohner import Bewohner
from .const import PLATFORMS

type WernerConfigEntry = ConfigEntry[Bewohner]


async def async_setup_entry(hass: HomeAssistant, entry: WernerConfigEntry) -> bool:
    """Einen Bewohner einrichten."""
    bewohner = Bewohner(hass, entry)
    entry.runtime_data = bewohner
    # Entitäten zuerst: sie stellen Einstellungen und Status nach einem Neustart wieder her.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await bewohner.async_start()
    entry.async_on_unload(bewohner.stop)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: WernerConfigEntry) -> None:
    """Aktivitätsquellen oder Grundlast wurden geändert."""
    entry.runtime_data.options_updated()


async def async_unload_entry(hass: HomeAssistant, entry: WernerConfigEntry) -> bool:
    """Einen Bewohner entfernen oder neu laden."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
