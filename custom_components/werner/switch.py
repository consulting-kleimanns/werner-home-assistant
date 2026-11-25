"""Schalter: Pause und Regeln."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import WernerConfigEntry
from .entity import WernerEntity

KEYS = (
    "active",
    "paused",
    "rule_morning",
    "rule_quiet",
    "rule_night",
    "consent_camera",
    "consent_microphone",
)


async def async_setup_entry(
    hass: HomeAssistant, entry: WernerConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Schalter anlegen."""
    async_add_entities(WernerSwitch(entry.runtime_data, key) for key in KEYS)


class WernerSwitch(WernerEntity, SwitchEntity, RestoreEntity):
    """Ein Schalter, der eine Einstellung des Bewohners steuert."""

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state in (STATE_ON, STATE_OFF):
            self.bewohner.restore_setting(self._key, last.state == STATE_ON)

    @property
    def is_on(self) -> bool:
        return bool(self.bewohner.settings[self._key])

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.bewohner.set_setting(self._key, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.bewohner.set_setting(self._key, False)
