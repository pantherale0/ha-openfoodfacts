"""Test the Open Food Facts service actions."""

from unittest.mock import MagicMock

import pytest
import requests
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.open_food_facts import async_setup
from custom_components.open_food_facts.const import (
    ATTR_BARCODE,
    ATTR_FIELDS,
    ATTR_PAGE,
    ATTR_PAGE_SIZE,
    ATTR_QUERY,
    ATTR_SORT_BY,
    DOMAIN,
    SERVICE_GET_PRODUCT,
    SERVICE_SEARCH_PRODUCTS,
)


async def test_get_product_success(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_openfoodfacts_api: MagicMock,
) -> None:
    """Test get_product successfully retrieves product data."""
    mock_openfoodfacts_api.product.get.return_value = {
        "code": "3017620422003",
        "product_name": "Nutella",
    }

    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_PRODUCT,
        {
            ATTR_BARCODE: "3017620422003",
            ATTR_FIELDS: ["product_name"],
        },
        blocking=True,
        return_response=True,
    )

    mock_openfoodfacts_api.product.get.assert_called_once_with(
        "3017620422003", fields=["product_name"]
    )
    assert response == {
        "product": {
            "code": "3017620422003",
            "product_name": "Nutella",
        }
    }


async def test_get_product_not_found(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_openfoodfacts_api: MagicMock,
) -> None:
    """Test get_product returns None when product is not found."""
    mock_openfoodfacts_api.product.get.return_value = None

    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_PRODUCT,
        {ATTR_BARCODE: "0000000000000"},
        blocking=True,
        return_response=True,
    )

    assert response == {"product": None}


async def test_get_product_invalid_barcode(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test get_product raises ServiceValidationError on blank barcode."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_PRODUCT,
            {ATTR_BARCODE: "   "},
            blocking=True,
            return_response=True,
        )


async def test_get_product_communication_error(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_openfoodfacts_api: MagicMock,
) -> None:
    """Test get_product handles communication exceptions."""
    mock_openfoodfacts_api.product.get.side_effect = (
        requests.exceptions.ConnectionError("Connection timed out")
    )

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_PRODUCT,
            {ATTR_BARCODE: "3017620422003"},
            blocking=True,
            return_response=True,
        )


async def test_search_products_success(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_openfoodfacts_api: MagicMock,
) -> None:
    """Test search_products returns search results."""
    mock_openfoodfacts_api.product.text_search.return_value = {
        "count": 1,
        "page": 1,
        "page_count": 1,
        "page_size": 20,
        "products": [{"code": "12345", "product_name": "Sparkling Water"}],
    }

    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_SEARCH_PRODUCTS,
        {
            ATTR_QUERY: "water",
            ATTR_PAGE: 1,
            ATTR_PAGE_SIZE: 20,
            ATTR_SORT_BY: "product_name",
        },
        blocking=True,
        return_response=True,
    )

    mock_openfoodfacts_api.product.text_search.assert_called_once_with(
        "water", page=1, page_size=20, sort_by="product_name"
    )
    assert response == {
        "count": 1,
        "page": 1,
        "page_count": 1,
        "page_size": 20,
        "products": [{"code": "12345", "product_name": "Sparkling Water"}],
    }


async def test_search_products_invalid_query(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test search_products raises ServiceValidationError on blank query."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_PRODUCTS,
            {ATTR_QUERY: "  "},
            blocking=True,
            return_response=True,
        )


async def test_search_products_communication_error(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_openfoodfacts_api: MagicMock,
) -> None:
    """Test search_products handles communication exceptions."""
    mock_openfoodfacts_api.product.text_search.side_effect = (
        requests.exceptions.HTTPError("500 Server Error")
    )

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_PRODUCTS,
            {ATTR_QUERY: "test"},
            blocking=True,
            return_response=True,
        )


async def test_service_called_when_not_loaded(
    hass: HomeAssistant,
) -> None:
    """
    Test service call when integration is not loaded.

    Should raise ServiceValidationError.
    """
    await async_setup(hass, {})

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_PRODUCT,
            {ATTR_BARCODE: "3017620422003"},
            blocking=True,
            return_response=True,
        )
