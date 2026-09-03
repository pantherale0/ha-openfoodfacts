"""Constants for open_food_facts."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "open_food_facts"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

DEFAULT_UPDATE_INTERVAL_HOURS = 1.0
