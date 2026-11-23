"""Zahlen: Uhrzeit für „Morgens nichts los“, Ruhestunden, Wartezeit."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import WernerConfigEntry
from .bewohner import Bewohner
from .entity import WernerEntity


@dataclass(frozen=True)
class _Def:
    key: str
    minimum: float
    maximum: float
    step: float
    unit: str | None


DEFS = (
    _Def("morning_until", 7, 12, 1, None),
    _Def("quiet_hours", 2, 8, 1, UnitOfTime.HOURS),
    _Def("wait_minutes", 5, 30, 5, UnitOfTime.MINUTES),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: WernerConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Zahlen anlegen."""
    async_add_entities(WernerNumber(entry.runtime_data, d) for d in DEFS)


class WernerNumber(WernerEntity, RestoreNumber):
    """Eine Zahl, die eine Einstellung des Bewohners steuert."""

    _attr_mode = NumberMode.BOX

    def __init__(self, bewohner: Bewohner, definition: _Def) -> None:
        super().__init__(bewohner, definition.key)
        self._attr_native_min_value = definition.minimum
        self._attr_native_max_value = definition.maximum
        self._attr_native_step = definition.step
        self._attr_native_unit_of_measurement = definition.unit

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self.bewohner.restore_setting(self._key, int(last.native_value))

    @property
    def native_value(self) -> float:
        return float(self.bewohner.settings[self._key])

    async def async_set_native_value(self, value: float) -> None:
        self.bewohner.set_setting(self._key, int(value))
