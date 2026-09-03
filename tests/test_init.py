"""Test integration setup and entry lifecycle."""

from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.open_food_facts import async_setup
from custom_components.open_food_facts.const import (
    DOMAIN,
    SERVICE_GET_PRODUCT,
    SERVICE_SEARCH_PRODUCTS,
)


async def test_async_setup(hass: HomeAssistant) -> None:
    """Test async_setup registers services without any config entries."""
    assert not hass.services.has_service(DOMAIN, SERVICE_GET_PRODUCT)
    assert not hass.services.has_service(DOMAIN, SERVICE_SEARCH_PRODUCTS)

    assert await async_setup(hass, {})

    assert hass.services.has_service(DOMAIN, SERVICE_GET_PRODUCT)
    assert hass.services.has_service(DOMAIN, SERVICE_SEARCH_PRODUCTS)


async def test_setup_and_unload_entry(
    hass: HomeAssistant,
    mock_openfoodfacts_api: MagicMock,
    config_entry: MockConfigEntry,
) -> None:
    """Test successful setup and unload of a config entry."""
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.runtime_data is mock_openfoodfacts_api

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.NOT_LOADED
