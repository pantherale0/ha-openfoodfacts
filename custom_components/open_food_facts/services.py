"""Service actions for Open Food Facts."""

from functools import partial
from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from .const import (
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


async def async_handle_get_product(
    hass: HomeAssistant,
    api: API,
    call: ServiceCall,
) -> ServiceResponse:
    """Handle get_product service action."""
    barcode: str = call.data[ATTR_BARCODE].strip()
    if not barcode:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="invalid_barcode",
        )

    fields: list[str] | None = call.data.get(ATTR_FIELDS)

    try:
        product: dict[str, Any] | None = await hass.async_add_executor_job(
            partial(api.product.get, barcode, fields=fields)
        )
    except (requests.exceptions.RequestException, ValueError) as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="communication_error",
            translation_placeholders={"error": str(err)},
        ) from err

    return {"product": product}


async def async_handle_search_products(
    hass: HomeAssistant,
    api: API,
    call: ServiceCall,
) -> ServiceResponse:
    """Handle search_products service action."""
    query: str = call.data[ATTR_QUERY].strip()
    if not query:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="invalid_query",
        )

    page: int = call.data.get(ATTR_PAGE, 1)
    page_size: int = call.data.get(ATTR_PAGE_SIZE, 20)
    sort_by: str | None = call.data.get(ATTR_SORT_BY)

    try:
        results: dict[str, Any] = await hass.async_add_executor_job(
            partial(
                api.product.text_search,
                query,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
            )
        )
    except (requests.exceptions.RequestException, ValueError) as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="communication_error",
            translation_placeholders={"error": str(err)},
        ) from err

    return {
        "count": results.get("count", 0),
        "page": results.get("page", page),
        "page_count": results.get("page_count", 0),
        "page_size": results.get("page_size", page_size),
        "products": results.get("products", []),
    }


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
