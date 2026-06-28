"""Data update coordinator for the CHMU Air Quality integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .air_quality_data import CHMUAirQuality, CHMUApiError
from .const import DEFAULT_SCAN_INTERVAL_MINUTES, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)

type CHMUConfigEntry = ConfigEntry[CHMUDataUpdateCoordinator]


class CHMUDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that polls the CHMI API for a single station."""

    def __init__(self, hass: HomeAssistant, entry: CHMUConfigEntry, station: str) -> None:
        """Initialise the coordinator."""
        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{station}",
            update_interval=timedelta(minutes=scan_interval),
        )
        self.station = station
        self._api = CHMUAirQuality(async_get_clientsession(hass))

    async def _async_update_data(self) -> dict:
        """Fetch the latest data for the configured station."""
        try:
            data = await self._api.get_station_data(self.station)
        except CHMUApiError as err:
            raise UpdateFailed(str(err)) from err

        if not data or not data.get("station_data"):
            raise UpdateFailed(f"No data returned for station '{self.station}'")

        return data

    @property
    def station_data(self) -> dict:
        """Return the processed station data dictionary."""
        return (self.data or {}).get("station_data") or {}

    @property
    def station_code(self) -> str:
        """Return the station code, falling back to the configured name."""
        return self.station_data.get("station_code") or self.station

    @property
    def device_info(self) -> dict:
        """Return device info linking entities to a single station device."""
        return {
            "identifiers": {(DOMAIN, self.station_code)},
            "name": self.station_data.get("station_name") or self.station,
            "manufacturer": MANUFACTURER,
            "model": self.station_data.get("classification"),
        }
