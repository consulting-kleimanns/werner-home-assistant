"""Sensoren: Status und letzte Aktivität des Bewohners."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from . import WernerConfigEntry
from .const import STATUSES
from .entity import WernerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: WernerConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Sensoren anlegen."""
    bewohner = entry.runtime_data
    async_add_entities([StatusSensor(bewohner, "status"), LastActivitySensor(bewohner, "last_activity")])


class StatusSensor(WernerEntity, SensorEntity, RestoreEntity):
    """Werners Status für diesen Bewohner."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATUSES

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            self.bewohner.restore_status(last.state, dict(last.attributes))

    @property
    def native_value(self) -> str:
        return self.bewohner.status

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "reason": self.bewohner.reason,
            "procedure": self.bewohner.procedure,
            "person_index": self.bewohner.person_index,
        }


class LastActivitySensor(WernerEntity, SensorEntity, RestoreEntity):
    """Wann Werner zuletzt etwas vom Bewohner bemerkt hat."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            self.bewohner.restore_last_activity(dt_util.parse_datetime(last.state))

    @property
    def native_value(self) -> datetime | None:
        return self.bewohner.last_activity
