"""Knöpfe: „Alles gut“ und „Ich brauche Hilfe“."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import WernerConfigEntry
from .entity import WernerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: WernerConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Knöpfe anlegen."""
    bewohner = entry.runtime_data
    async_add_entities([AllGoodButton(bewohner, "all_good"), HelpButton(bewohner, "help")])


class AllGoodButton(WernerEntity, ButtonEntity):
    """Beantwortet eine Nachfrage und merkt sich Aktivität."""

    async def async_press(self) -> None:
        self.bewohner.all_good()


class HelpButton(WernerEntity, ButtonEntity):
    """Informiert sofort die Vertrauenspersonen – auch wenn Werner pausiert ist."""

    async def async_press(self) -> None:
        self.bewohner.help()
