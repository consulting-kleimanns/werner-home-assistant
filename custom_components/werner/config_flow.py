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

from .geraete import suggest_notify
from .const import (
    CONF_BASELOAD,
    CONF_BATTERY_SOC,
    CONF_CONSENT,
    CONF_CREATED_BY,
    CONF_CHARGE_MODE,
    CONF_GRID_ENERGY,
    CONF_GRID_POWER,
    CONF_NAME,
    CONF_NOTIFY,
    CONF_PERSON,
    CONF_PV_KWP,
    CONF_PV_POWER,
    CONF_SIGNAL_URL,
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

    async def async_step_werner_ui(
        self, data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Bewohner aus „Mein Zuhause“ (geprüft in websocket.py)."""
        await self.async_set_unique_id(data[CONF_PERSON])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=data[CONF_NAME],
            data={k: data[k] for k in (CONF_NAME, CONF_PERSON, CONF_NOTIFY, CONF_CONSENT, CONF_CREATED_BY)},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Nur die Person wählen – Name und Handy findet Werner selbst."""
        errors: dict[str, str] = {}
        taken = [e.unique_id or e.data.get(CONF_PERSON) for e in self._async_current_entries()]
        persons = [s.entity_id for s in self.hass.states.async_all("person") if s.entity_id not in taken]
        if not persons:
            return self.async_abort(
                reason="no_person" if not taken else "all_persons_configured"
            )

        if user_input is not None:
            person = user_input[CONF_PERSON]
            state = self.hass.states.get(person)
            name = (user_input.get(CONF_NAME) or "").strip()
            if not name and state is not None:
                name = state.name.split(" ")[0]
            notify = (user_input.get(CONF_NOTIFY) or "").strip().removeprefix(NOTIFY_PREFIX)
            if not notify:
                notify = suggest_notify(self.hass, person)

            if state is None:
                errors[CONF_PERSON] = "person_missing"
            if not name:
                errors[CONF_NAME] = "name_missing"
            if notify and not self.hass.services.has_service("notify", notify):
                errors[CONF_NOTIFY] = "notify_not_found"

            if not errors:
                await self.async_set_unique_id(person)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={CONF_NAME: name, CONF_PERSON: person, CONF_NOTIFY: notify},
                )

        phones = sorted(
            s for s in self.hass.services.async_services_for_domain("notify") if s.startswith("mobile_app_")
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_PERSON, default=persons[0]): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="person", exclude_entities=taken)
                ),
                vol.Optional(CONF_NAME): selector.TextSelector(),
                vol.Optional(CONF_NOTIFY): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=p, label=p.removeprefix("mobile_app_").replace("_", " ")
                            )
                            for p in phones
                        ],
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
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
                vol.Optional(CONF_SIGNAL_URL): selector.TextSelector(),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, dict(options)),
        )
