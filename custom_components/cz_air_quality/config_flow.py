"""Config flow for the CHMU Air Quality integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .air_quality_data import CHMUAirQuality, CHMUApiError
from .const import CONF_STOP_SEL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class CHMUConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CHMU Air Quality."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            station = user_input[CONF_STOP_SEL]
            await self.async_set_unique_id(station)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=station, data=user_input)

        try:
            api = CHMUAirQuality(async_get_clientsession(self.hass))
            station_names = await api.get_all_station_names()
        except CHMUApiError:
            _LOGGER.exception("Unable to fetch station list from CHMI")
            return self.async_abort(reason="cannot_connect")

        if not station_names:
            return self.async_abort(reason="no_stations")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_STOP_SEL): SelectSelector(
                    SelectSelectorConfig(
                        options=sorted(station_names),
                        mode=SelectSelectorMode.DROPDOWN,
                        sort=True,
                        custom_value=False,
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
