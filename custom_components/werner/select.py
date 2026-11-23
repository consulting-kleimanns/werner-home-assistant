"""Auswahl: auf welchem Weg Werner eine Vertrauensperson erreicht."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import WernerConfigEntry
from .const import PERSON_COUNT, WAYS
from .entity import WernerPersonEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: WernerConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Auswahlfelder anlegen."""
    async_add_entities(
        WernerWaySelect(entry.runtime_data, n, "way") for n in range(1, PERSON_COUNT + 1)
    )


class WernerWaySelect(WernerPersonEntity, SelectEntity, RestoreEntity):
    """Weg zur Vertrauensperson: aus, Home-Assistant-App, Signal, E-Mail."""

    _attr_options = WAYS

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state in WAYS:
            self.bewohner.restore_setting(self._key, last.state)

    @property
    def current_option(self) -> str:
        return str(self.bewohner.settings[self._key])

    async def async_select_option(self, option: str) -> None:
        self.bewohner.set_setting(self._key, option)
