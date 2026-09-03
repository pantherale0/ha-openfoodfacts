"""
Custom integration to integrate open_food_facts with Home Assistant.

For more details about this integration, please refer to:
https://github.com/pantherale0/ha-openfoodfacts
"""

from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from openfoodfacts import API

from .const import DEFAULT_USER_AGENT, DOMAIN
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

type OpenFoodFactsConfigEntry = ConfigEntry[API]

PLATFORMS: list[Platform] = []

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """
    Register the service actions.

    Returns:
        True once the actions are registered.

    """
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpenFoodFactsConfigEntry,
) -> bool:
    """
    Set up a config entry.

    Returns:
        True once the API client is initialized and attached to runtime_data.

    """
    api = API(user_agent=DEFAULT_USER_AGENT)
    entry.runtime_data = api
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: OpenFoodFactsConfigEntry,
) -> bool:
    """
    Unload a config entry.

    Returns:
        True once unloaded.

    """
    return True
