"""Einrichtungs-Assistent für Werner: ein Eintrag je Bewohner."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import selector

from .const import CONF_NAME, CONF_NOTIFY, CONF_PERSON, DOMAIN

NOTIFY_PREFIX = "notify."


class WernerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Bewohner hinzufügen."""

    VERSION = 1

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
