"""Constants for open_food_facts."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "open_food_facts"

DEFAULT_USER_AGENT = (
    "HomeAssistant-OpenFoodFacts (https://github.com/pantherale0/ha-openfoodfacts)"
)

SERVICE_GET_PRODUCT = "get_product"
SERVICE_SEARCH_PRODUCTS = "search_products"

ATTR_BARCODE = "barcode"
ATTR_FIELDS = "fields"
ATTR_PAGE = "page"
ATTR_PAGE_SIZE = "page_size"
ATTR_QUERY = "query"
ATTR_SORT_BY = "sort_by"
