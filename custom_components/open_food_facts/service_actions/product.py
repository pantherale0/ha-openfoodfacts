"""Product retrieval and search service actions for Open Food Facts."""

from functools import partial
from typing import TYPE_CHECKING, Any

import requests
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.open_food_facts.const import (
    ATTR_BARCODE,
    ATTR_FIELDS,
    ATTR_PAGE,
    ATTR_PAGE_SIZE,
    ATTR_QUERY,
    ATTR_SORT_BY,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
    from openfoodfacts import API


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
