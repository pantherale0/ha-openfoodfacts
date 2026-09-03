"""Shared fixtures for the open_food_facts tests."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.open_food_facts.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom integrations in every test."""


@pytest.fixture
def mock_openfoodfacts_api() -> Generator[MagicMock]:
    """Mock the openfoodfacts.API class."""
    with patch(
        "custom_components.open_food_facts.API",
        autospec=True,
    ) as mock_api_class:
        mock_instance = MagicMock()
        mock_api_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Return a config entry for this integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Open Food Facts",
        unique_id=DOMAIN,
        data={},
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_openfoodfacts_api: MagicMock,
    config_entry: MockConfigEntry,
) -> MockConfigEntry:
    """
    Set up the integration from a config entry.

    Returns:
        The config entry, now loaded.

    """
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
