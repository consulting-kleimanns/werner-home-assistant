"""Werner – ein freundlicher Aufpasser für Senioren.

Jeder Bewohner ist ein eigener Konfigurationseintrag. Die Warnlogik
(Nachfragen, Vertrauenspersonen informieren) folgt in den nächsten Versionen.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Einen Bewohner einrichten."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = dict(entry.data)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Einen Bewohner entfernen."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
