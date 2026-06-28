"""Sensor platform for the CHMU Air Quality integration."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import AQI_ATTRIBUTES, AQI_OPTIONS, ICON_UPDATE, MEASUREMENT_DEFINITIONS
from .coordinator import CHMUConfigEntry, CHMUDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: CHMUConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors for a config entry."""
    coordinator = config_entry.runtime_data

    entities: list[SensorEntity] = [
        AirQualitySensor(coordinator),
        StationSensor(coordinator),
        UpdateSensor(coordinator),
    ]
    entities.extend(
        MeasurementSensor(coordinator, definition)
        for definition in MEASUREMENT_DEFINITIONS
    )

    async_add_entities(entities)


class CHMUBaseEntity(CoordinatorEntity[CHMUDataUpdateCoordinator], SensorEntity):
    """Base entity wiring up the coordinator and device info."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: CHMUDataUpdateCoordinator) -> None:
        """Initialise the base entity."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info


class AirQualitySensor(CHMUBaseEntity):
    """Sensor for the air quality index."""

    _attr_translation_key = "air_quality_index"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = AQI_OPTIONS

    def __init__(self, coordinator: CHMUDataUpdateCoordinator) -> None:
        """Initialise the air quality index sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.station_code}_aqi"

    @property
    def native_value(self) -> str | None:
        """Return the air quality index value."""
        index = self.coordinator.station_data.get("air_quality_index")
        return index if index in AQI_OPTIONS else None

    @property
    def extra_state_attributes(self) -> dict:
        """Return colour and recommendation attributes for the index."""
        return AQI_ATTRIBUTES.get(self.native_value, {})


class MeasurementSensor(CHMUBaseEntity):
    """Sensor for an individual pollutant measurement."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    def __init__(
        self, coordinator: CHMUDataUpdateCoordinator, definition: dict
    ) -> None:
        """Initialise a measurement sensor from its definition."""
        super().__init__(coordinator)
        self._key = definition["key"]
        self._attr_name = definition["name"]
        self._attr_device_class = definition["device_class"]
        self._attr_unique_id = f"{coordinator.station_code}_{self._key}"

    @property
    def native_value(self) -> float | None:
        """Return the measured concentration."""
        return self.coordinator.station_data.get(self._key)


class StationSensor(CHMUBaseEntity):
    """Diagnostic sensor exposing station metadata."""

    _attr_translation_key = "station"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: CHMUDataUpdateCoordinator) -> None:
        """Initialise the station metadata sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.station_code}_station"

    @property
    def native_value(self) -> str | None:
        """Return the station name."""
        return self.coordinator.station_data.get("station_name")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional station metadata."""
        data = self.coordinator.station_data
        return {
            "station_code": data.get("station_code"),
            "region": data.get("region"),
            "classification": data.get("classification"),
            "owner": data.get("owner"),
        }


class UpdateSensor(CHMUBaseEntity):
    """Diagnostic sensor exposing the timestamp of the source data."""

    _attr_translation_key = "data_updated"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = ICON_UPDATE

    def __init__(self, coordinator: CHMUDataUpdateCoordinator) -> None:
        """Initialise the data-updated sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.station_code}_updated"

    @property
    def native_value(self) -> datetime | None:
        """Return the timestamp reported by the API as a datetime."""
        raw = (self.coordinator.data or {}).get("updated")
        if not raw:
            return None
        return dt_util.parse_datetime(raw)
