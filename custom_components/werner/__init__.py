"""Werner – ein freundlicher Aufpasser für Senioren.

Jeder Bewohner ist ein eigener Konfigurationseintrag mit eigenem Gerät,
eigenen Einstellungen und eigenem Ablauf. Die Oberfläche „Mein Zuhause“
bringt die Integration selbst mit: als Bereich in der Seitenleiste und als
Karte für Dashboards.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .bewohner import Bewohner
from .websocket import async_register_commands
from .const import (
    ATTR_CONFIG_ENTRY_ID,
    ATTR_PERSON,
    ATTR_REASON,
    DOMAIN,
    FRONTEND_FILE,
    FRONTEND_URL_BASE,
    PANEL_ICON,
    PANEL_TITLE,
    PANEL_URL_PATH,
    PERSON_COUNT,
    PLATFORMS,
    SERVICE_ASK,
    SERVICE_TEST_PERSON,
    WEBCOMPONENT,
)

_LOGGER = logging.getLogger(__name__)

type WernerConfigEntry = ConfigEntry[Bewohner]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

FRONTEND_DIR = Path(__file__).parent / "frontend"

SCHEMA_TEST_PERSON = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_PERSON): vol.All(vol.Coerce(int), vol.Range(min=1, max=PERSON_COUNT)),
    }
)
SCHEMA_ASK = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Optional(ATTR_REASON): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Oberfläche und Dienste einmal für alle Bewohner anmelden."""
    await _async_register_frontend(hass)
    async_register_commands(hass)

    def _bewohner(call: ServiceCall) -> Bewohner:
        entry = hass.config_entries.async_get_entry(call.data[ATTR_CONFIG_ENTRY_ID])
        if entry is None or entry.domain != DOMAIN or entry.state is not ConfigEntryState.LOADED:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="resident_not_found"
            )
        return entry.runtime_data

    async def _test_person(call: ServiceCall) -> ServiceResponse:
        return await _bewohner(call).async_test_person(call.data[ATTR_PERSON])

    async def _ask(call: ServiceCall) -> None:
        bewohner = _bewohner(call)
        bewohner.ask(call.data.get(ATTR_REASON) or "Werner möchte wissen, ob bei Ihnen alles in Ordnung ist.")

    hass.services.async_register(
        DOMAIN,
        SERVICE_TEST_PERSON,
        _test_person,
        schema=SCHEMA_TEST_PERSON,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(DOMAIN, SERVICE_ASK, _ask, schema=SCHEMA_ASK)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """„Mein Zuhause“ ausliefern: Seitenleiste und Karte für Dashboards."""
    if hass.http is None or "frontend" not in hass.config.components:
        return
    from homeassistant.components import frontend, panel_custom  # noqa: PLC0415
    from homeassistant.components.http import StaticPathConfig  # noqa: PLC0415

    script = FRONTEND_DIR / FRONTEND_FILE
    version = await hass.async_add_executor_job(
        lambda: hashlib.sha256(script.read_bytes()).hexdigest()[:10]
    )
    url = f"{FRONTEND_URL_BASE}/{FRONTEND_FILE}?v={version}"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL_BASE, str(FRONTEND_DIR), cache_headers=False)]
    )
    # Als Karte in jedem Dashboard nutzbar: type: custom:werner-mein-zuhause
    frontend.add_extra_js_url(hass, url)
    try:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_URL_PATH,
            webcomponent_name=WEBCOMPONENT,
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            module_url=url,
            require_admin=False,
            config={},
        )
    except ValueError:
        _LOGGER.warning("Der Bereich /%s ist schon belegt", PANEL_URL_PATH)


async def async_setup_entry(hass: HomeAssistant, entry: WernerConfigEntry) -> bool:
    """Einen Bewohner einrichten."""
    bewohner = Bewohner(hass, entry)
    entry.runtime_data = bewohner
    # Entitäten zuerst: sie stellen Einstellungen und Status nach einem Neustart wieder her.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await bewohner.async_start()
    entry.async_on_unload(bewohner.stop)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: WernerConfigEntry) -> None:
    """Aktivitätsquellen, Grundlast oder Energie-Sensoren wurden geändert."""
    entry.runtime_data.options_updated()


async def async_unload_entry(hass: HomeAssistant, entry: WernerConfigEntry) -> bool:
    """Einen Bewohner entfernen oder neu laden."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
