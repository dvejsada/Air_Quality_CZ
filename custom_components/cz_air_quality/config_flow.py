"""Config and options flow for the CHMU Air Quality integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .air_quality_data import CHMUAirQuality, CHMUApiError
from .const import (
    CONF_STOP_SEL,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    MAX_SCAN_INTERVAL_MINUTES,
    MIN_SCAN_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)


def _station_schema(options: list[str]) -> vol.Schema:
    """Build the station-selection schema."""
    return vol.Schema(
        {
            vol.Required(CONF_STOP_SEL): SelectSelector(
                SelectSelectorConfig(
                    options=options,
                    mode=SelectSelectorMode.DROPDOWN,
                    sort=True,
                    custom_value=False,
                )
            )
        }
    )


class CHMUConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CHMU Air Quality."""

    VERSION = 1

    async def _async_station_options(self) -> list[str]:
        """Fetch the sorted list of station names from CHMI."""
        api = CHMUAirQuality(async_get_clientsession(self.hass))
        return sorted(await api.get_all_station_names())

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            station = user_input[CONF_STOP_SEL]
            await self.async_set_unique_id(station)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=station, data=user_input)

        try:
            options = await self._async_station_options()
        except CHMUApiError:
            _LOGGER.exception("Unable to fetch station list from CHMI")
            return self.async_abort(reason="cannot_connect")

        if not options:
            return self.async_abort(reason="no_stations")

        return self.async_show_form(step_id="user", data_schema=_station_schema(options))

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the selected station."""
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            station = user_input[CONF_STOP_SEL]
            # Block switching to a station already configured by another entry.
            for entry in self._async_current_entries():
                if (
                    entry.entry_id != reconfigure_entry.entry_id
                    and entry.unique_id == station
                ):
                    return self.async_abort(reason="already_configured")

            await self.async_set_unique_id(station)
            return self.async_update_reload_and_abort(
                reconfigure_entry,
                unique_id=station,
                title=station,
                data_updates={CONF_STOP_SEL: station},
            )

        try:
            options = await self._async_station_options()
        except CHMUApiError:
            _LOGGER.exception("Unable to fetch station list from CHMI")
            return self.async_abort(reason="cannot_connect")

        if not options:
            return self.async_abort(reason="no_stations")

        schema = self.add_suggested_values_to_schema(
            _station_schema(options),
            {CONF_STOP_SEL: reconfigure_entry.data.get(CONF_STOP_SEL)},
        )
        return self.async_show_form(step_id="reconfigure", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> CHMUOptionsFlow:
        """Return the options flow handler."""
        return CHMUOptionsFlow()


class CHMUOptionsFlow(OptionsFlow):
    """Handle the options flow (scan interval)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL_MINUTES,
                        max=MAX_SCAN_INTERVAL_MINUTES,
                        step=5,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
