"""Einrichtungs-Assistent für Werner: ein Eintrag je Bewohner."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_BASELOAD,
    CONF_BATTERY_SOC,
    CONF_CHARGE_MODE,
    CONF_GRID_ENERGY,
    CONF_GRID_POWER,
    CONF_NAME,
    CONF_NOTIFY,
    CONF_PERSON,
    CONF_PV_KWP,
    CONF_PV_POWER,
    CONF_SOURCES,
    CONF_VEHICLE_NAME,
    CONF_VEHICLE_SOC,
    CONF_WEATHER,
    DEFAULT_BASELOAD,
    DOMAIN,
)

NOTIFY_PREFIX = "notify."


class WernerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Bewohner hinzufügen."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> WernerOptionsFlow:
        """Optionen: Aktivitätsquellen und Grundlast."""
        return WernerOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Name, Person und Handy des Bewohners abfragen."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            notify = (user_input.get(CONF_NOTIFY) or "").strip()
            if notify.startswith(NOTIFY_PREFIX):
                notify = notify[len(NOTIFY_PREFIX):]

            if not name:
                errors[CONF_NAME] = "name_missing"
            if notify and not self.hass.services.has_service("notify", notify):
                errors[CONF_NOTIFY] = "notify_not_found"

            if not errors:
                await self.async_set_unique_id(user_input[CONF_PERSON])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_PERSON: user_input[CONF_PERSON],
                        CONF_NOTIFY: notify,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): selector.TextSelector(),
                vol.Required(CONF_PERSON): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="person")
                ),
                vol.Optional(CONF_NOTIFY): selector.TextSelector(),
            }
        )
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )


class WernerOptionsFlow(OptionsFlow):
    """Woran Werner Aktivität erkennt – und freiwillig Energie und Auto."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Aktivitätsquellen, Grundlast sowie Energie- und Auto-Sensoren einstellen."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        def entity(domain: str | list[str]) -> selector.EntitySelector:
            return selector.EntitySelector(selector.EntitySelectorConfig(domain=domain))

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SOURCES, default=list(options.get(CONF_SOURCES, []))
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "binary_sensor", "device_tracker", "media_player", "light", "switch"],
                        multiple=True,
                    )
                ),
                vol.Required(
                    CONF_BASELOAD, default=options.get(CONF_BASELOAD, DEFAULT_BASELOAD)
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=5000,
                        step=10,
                        unit_of_measurement="W",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_WEATHER): entity("weather"),
                vol.Optional(CONF_GRID_POWER): entity("sensor"),
                vol.Optional(CONF_GRID_ENERGY): entity("sensor"),
                vol.Optional(CONF_PV_POWER): entity("sensor"),
                vol.Optional(CONF_PV_KWP): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=30, step=0.1, unit_of_measurement="kWp",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_BATTERY_SOC): entity("sensor"),
                vol.Optional(CONF_VEHICLE_NAME): selector.TextSelector(),
                vol.Optional(CONF_VEHICLE_SOC): entity("sensor"),
                vol.Optional(CONF_CHARGE_MODE): entity(["select", "input_select"]),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, dict(options)),
        )
