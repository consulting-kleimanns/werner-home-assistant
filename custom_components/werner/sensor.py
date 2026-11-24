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
    # Wird von der Oberfläche gelesen, gehört aber nicht in die Datenbank.
    _unrecorded_attributes = frozenset(
        {"entities", "sources", "baseload_w", "energy", "person", "resident", "notify", "entry_id"}
    )

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
        b = self.bewohner
        return {
            "reason": b.reason,
            "about": b.about,
            "procedure": b.procedure,
            "person_index": b.person_index,
            "resident": b.name,
            "entry_id": b.entry.entry_id,
            "person": b.person,
            "notify": bool(b.notify),
            "consent": b.consent,
            "entities": dict(b.entity_ids),
            "sources": b.sources,
            "baseload_w": b.baseload,
            "energy": b.energy,
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
