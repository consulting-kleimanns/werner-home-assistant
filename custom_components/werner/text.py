"""Texte: Name, Gerät, Handynummer und E-Mail der Vertrauenspersonen."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import WernerConfigEntry
from .const import PERSON_COUNT, PERSON_FIELDS
from .entity import WernerPersonEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: WernerConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Textfelder anlegen."""
    async_add_entities(
        WernerText(entry.runtime_data, n, field)
        for n in range(1, PERSON_COUNT + 1)
        for field in PERSON_FIELDS
    )


class WernerText(WernerPersonEntity, TextEntity, RestoreEntity):
    """Ein Textfeld einer Vertrauensperson."""

    _attr_mode = TextMode.TEXT
    _attr_native_max = 100

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            self.bewohner.restore_setting(self._key, last.state)

    @property
    def native_value(self) -> str:
        return str(self.bewohner.settings[self._key])

    async def async_set_value(self, value: str) -> None:
        self.bewohner.set_setting(self._key, value.strip())
