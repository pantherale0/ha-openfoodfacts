"""Service actions for Open Food Facts."""

from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import ServiceValidationError

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

from .product import async_handle_get_product, async_handle_search_products

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
    from openfoodfacts import API

GET_PRODUCT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_BARCODE): cv.string,
        vol.Optional(ATTR_FIELDS): vol.All(cv.ensure_list, [cv.string]),
    }
)

SEARCH_PRODUCTS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_QUERY): cv.string,
        vol.Optional(ATTR_PAGE, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
        vol.Optional(ATTR_PAGE_SIZE, default=20): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=100)
        ),
        vol.Optional(ATTR_SORT_BY): cv.string,
    }
)


def _async_get_api(hass: HomeAssistant) -> API:
    """Get the loaded Open Food Facts API client."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="not_loaded",
        )
    return entries[0].runtime_data


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register Open Food Facts service actions."""

    async def handle_get_product(call: ServiceCall) -> ServiceResponse:
        api = _async_get_api(hass)
        return await async_handle_get_product(hass, api, call)

    async def handle_search_products(call: ServiceCall) -> ServiceResponse:
        api = _async_get_api(hass)
        return await async_handle_search_products(hass, api, call)

    if not hass.services.has_service(DOMAIN, SERVICE_GET_PRODUCT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_PRODUCT,
            handle_get_product,
            schema=GET_PRODUCT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SEARCH_PRODUCTS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEARCH_PRODUCTS,
            handle_search_products,
            schema=SEARCH_PRODUCTS_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
