from __future__ import annotations

from homeassistant.core import HomeAssistant
from .air_quality_data import CHMUAirQuality
from collections.abc import Callable
from .const import DOMAIN


# Definice měření - mapování klíčů na názvy a device class identifikátory
MEASUREMENT_DEFINITIONS = [
    {"key": "so2_1h", "name": "SO2", "code": "SO2"},
    {"key": "no2_1h", "name": "NO2", "code": "NO2"},
    {"key": "co_8h", "name": "CO", "code": "CO"},
    {"key": "pm10_1h", "name": "PM10 1h", "code": "PM10"},
    {"key": "pm10_24h", "name": "PM10 24h", "code": "PM10"},
    {"key": "pm25_1h", "name": "PM2.5", "code": "PM2_5"},
    {"key": "o3_1h", "name": "O3", "code": "O3"},
]


class AirQuality:
    """Setting Air Quality Station as device."""

    def __init__(self, hass: HomeAssistant, station: str, data) -> None:
        """Initialize air quality station."""
        self._hass: HomeAssistant = hass
        self._station: str = station
        self._callbacks = set()
        self.data: dict = data

    @property
    def device_info(self):
        """Provides a device info."""
        return {
            "identifiers": {(DOMAIN, self.station_code)},
            "name": self.name,
            "manufacturer": "Czech Hydrometeorological Institute",
            "model": self.classification,
        }

    @property
    def name(self) -> str:
        """Provides name for station."""
        if self.data and self.data.get("station_data"):
            return self.data["station_data"].get("station_name", self._station)
        return self._station

    @property
    def station_code(self) -> str:
        """Returns code of the station."""
        if self.data and self.data.get("station_data"):
            return self.data["station_data"].get("station_code", "")
        return ""

    @property
    def index(self) -> str:
        """Returns air quality index."""
        if self.data and self.data.get("station_data"):
            return self.data["station_data"].get("air_quality_index", "")
        return ""

    @property
    def region(self) -> str:
        """Returns region of the station."""
        if self.data and self.data.get("station_data"):
            return self.data["station_data"].get("region", "")
        return ""

    @property
    def owner(self) -> str:
        """Returns owner of the station."""
        if self.data and self.data.get("station_data"):
            return self.data["station_data"].get("owner", "")
        return ""

    @property
    def classification(self) -> str:
        """Returns classification of the station."""
        if self.data and self.data.get("station_data"):
            return self.data["station_data"].get("classification", "")
        return ""

    @property
    def measurements(self) -> list:
        """Returns list of available measurements from the station."""
        result = []
        if self.data and self.data.get("station_data"):
            station_data = self.data["station_data"]
            for measurement in MEASUREMENT_DEFINITIONS:
                key = measurement["key"]
                value = station_data.get(key)
                result.append({
                    "key": key,
                    "name": measurement["name"],
                    "code": measurement["code"],
                    "value": value,
                    "available": value is not None,
                })
        return result

    @property
    def data_updated(self) -> str:
        """Timestamp of the last update of data."""
        if self.data:
            return self.data.get("updated", "")
        return ""

    @property
    def aqi_color(self) -> str:
        """Returns AQI color indicator."""
        if self.data and self.data.get("station_data"):
            return self.data["station_data"].get("limitPassedColor_aqi", "")
        return ""

    async def async_update(self) -> None:
        """Updates the data from API."""
        data = await self._hass.async_add_executor_job(
            CHMUAirQuality.get_station_data, self._station
        )
        if data and data.get("updated") and self.data_updated != data["updated"]:
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
