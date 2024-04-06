from __future__ import annotations

from homeassistant.core import HomeAssistant
from .air_quality_data import CHMUAirQuality
from collections.abc import Callable
from .const import DOMAIN


class AirQuality:
    """Setting Air Quality Station as device."""

    def __init__(self, hass: HomeAssistant, station: str) -> None:
        """Initialize departure board."""
        self._hass: HomeAssistant = hass
        self._station: str = station
        self._callbacks = set()
        self.data: dict = {}

    @property
    def device_info(self):
        """ Provides a device info. """
        return {"identifiers": {(DOMAIN, self._station)}, "name": self.name, "manufacturer": "Czech Hydrometeorological Institute"}

    @property
    def name(self) -> str:
        """Provides name for station."""
        return self._station

    @property
    def index(self) -> str:
        """ Returns air quality index."""
        return self.data["station_data"]["Ix"]

    @property
    def latitude(self) -> str:
        """ Returns latitude of the station."""
        return self.data["station_data"]["Lat"]

    @property
    def longitude(self) -> str:
        """Returns longitude of the station."""
        return self.data["station_data"]["Lon"]

    @property
    def owner(self):
        return self.data["station_data"]["Owner"]

    @property
    def code(self) -> str:
        """Returns code of the station"""
        return self.data["station_data"]["Code"]

    @property
    def classification(self) -> tuple:
        """ Returns classification of the station."""
        return self.data["station_data"]["Classif"]

    @property
    def measurements(self) -> list:
        """ Returns measurement from the station."""
        return self.data["station_data"]["Components"]

    @property
    def data_updated(self) -> str:
        """ Timestamp of the last update of data"""
        return self.data["updated"]

    async def async_update(self) -> None:
        """ Updates the data from API."""
        data = await self._hass.async_add_executor_job(CHMUAirQuality.update_info, self._station)
        if self.data_updated != data["updated"]:
            self.data = data
            await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when there are new data."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    async def publish_updates(self) -> None:
        """Schedule call to all registered callbacks."""
        for callback in self._callbacks:
            callback()
