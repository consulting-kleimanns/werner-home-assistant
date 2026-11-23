"""Gemeinsame Basis der Werner-Entitäten."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .bewohner import Bewohner
from .const import DOMAIN, signal_update


class WernerEntity(Entity):
    """Entität eines Bewohners – alle hängen am Gerät „Werner · <Name>“."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, bewohner: Bewohner, key: str) -> None:
        self.bewohner = bewohner
        self._key = key
        entry_id = bewohner.entry.entry_id
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"Werner · {bewohner.name}",
            manufacturer="Werner",
            model="Bewohner",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        """Bei Änderungen des Bewohners neu anzeigen."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal_update(self.bewohner.entry.entry_id), self.async_write_ha_state
            )
        )


class WernerPersonEntity(WernerEntity):
    """Einstellung einer Vertrauensperson (1–3)."""

    def __init__(self, bewohner: Bewohner, n: int, field: str) -> None:
        super().__init__(bewohner, f"person_{n}_{field}")
        self._attr_translation_key = f"person_{field}"
        self._attr_translation_placeholders = {"n": str(n)}
