import voluptuous as vol

import logging
from typing import Any, Tuple, Dict

from .const import DOMAIN, CONF_STOP_SEL
from homeassistant.const import STATION_LIST
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import selector


_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> tuple[dict[str, str], dict]:
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    pass


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    VERSION = 1

    async def async_step_user(self, user_input=None):

        data_schema: dict = {}

        data_schema[CONF_STOP_SEL] = selector({
                "select": {
                    "options": STATION_LIST,
                    "mode": "dropdown",
                    "sort": True,
                    "custom_value": True
                }
            })

        # Set dict for errors
        errors: dict = {}

        # Steps to take if user input is received
        if user_input is not None:
            try:
                info, data = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=user_input[CONF_STOP_SEL])

            except CannotConnect:
                _LOGGER.exception("Cannot download data, check your internet connection.")
                errors["base"] = "cannot_connect"

            except StationNotFound:
                errors[CONF_STOP_SEL] = "station_not_in_list"

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unknown exception")
                errors["base"] = "Unknown exception"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect for unknown reason."""


class StationNotFound(exceptions.HomeAssistantError):
    """Error to indicate wrong stop was provided."""


