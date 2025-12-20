"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from datetime import timedelta

from .const import DOMAIN, ICON_UPDATE
from homeassistant.const import EntityCategory


SCAN_INTERVAL = timedelta(seconds=900)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    air_quality_station = hass.data[DOMAIN][config_entry.entry_id]
    new_entities = []

    # Set entities for air quality and measurements
    new_entities.append(AirQualitySensor(air_quality_station))
    for i in range(len(air_quality_station.measurements)):
        new_entities.append(MeasurementSensor(i, air_quality_station))

    # Set diagnostic entities
    new_entities.append(StationSensor(air_quality_station))
    new_entities.append(UpdateSensor(air_quality_station))

    # Add all entities to HA
    async_add_entities(new_entities)


class AirQualitySensor(SensorEntity):
    """Sensor for air quality index."""
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, aq_station):
        self._aq_station = aq_station
        self._attr_unique_id = f"{self._aq_station.station_code}_aqi"

    @property
    def device_info(self) -> str:
        """Return information to link this entity with the correct device."""
        return self._aq_station.device_info

    @property
    def native_value(self) -> str:
        """ Returns name of the route as state."""
        return self._aq_station.index

    @property
    def extra_state_attributes(self) -> dict:
        """ Returns dictionary of additional state attributes"""
        extr_attr = {}
        match self._aq_station.index:
            case "1A":
                extr_attr = {"Color": "009900", "ColorText": "000000", "Description": "velmi dobrá", "Recommendation":"Ideální podmínky pro pobyt venku"}
            case "1B":
                extr_attr = {"Color": "00CC00", "ColorText": "000000", "Description": "dobrá", "Recommendation":"Venkovní aktivity bez omezení"}
            case "2A":
                extr_attr = {"Color": "FFF200", "ColorText": "000000", "Description": "přijatelná", "Recommendation":"Venkovní aktivity bez omezení"}
            case "2B":
                extr_attr = {"Color": "FAA61A", "ColorText": "000000", "Description": "přijatelná", "Recommendation":"Není třeba měnit své obvyklé aktivity venku."}
            case "3A":
                extr_attr = {"Color": "ED1C24", "ColorText": "FFFFFF", "Description": "zhoršená", "Recommendation":"Zvažte snížení nebo odložení/přesunutí namáhavé činnosti venku, pokud se objeví příznaky, jako je kašel a podráždění krku."}
            case "3B":
                extr_attr = {"Color": "671F20", "ColorText": "FFFFFF", "Description": "špatná", "Recommendation":"Omezte nebo odložte namáhavé činnosti venku, zvláště když zaznamenáte jakékoliv nepříjemné pocity a příznaky jako je dráždění v krku, pálení očí kašel apod."}
            case "0":
                extr_attr = {"Color": "FFFFFF", "ColorText": "000000", "Description": "neúplná data"}
            case "-1":
                extr_attr = {"Color": "CFCFCF", "ColorText": "000000", "Description": "index nestanoven"}
        return extr_attr

    @property
    def name(self) -> str:
        """Returns entity name"""
        return f"AQ Index"

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._aq_station.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._aq_station.remove_callback(self.async_write_ha_state)


class MeasurementSensor(SensorEntity):
    """Sensor for air quality measurement."""
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, measurement_index: int, aq_station):
        self._measurement_index = measurement_index
        self._aq_station = aq_station
        measurement = self._aq_station.measurements[measurement_index]
        self._measurement_key = measurement["key"]
        self._measurement_name = measurement["name"]
        self._measurement_code = measurement["code"]
        self._attr_unique_id = f"{self._aq_station.station_code}_{self._measurement_key}"

    @property
    def device_info(self) -> str:
        """Return information to link this entity with the correct device."""
        return self._aq_station.device_info

    @property
    def native_value(self):
        """Returns measurement value as state if available."""
        measurements = self._aq_station.measurements
        if self._measurement_index < len(measurements):
            measurement = measurements[self._measurement_index]
            return measurement.get("value")
        return None

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Returns device class based on measurement code."""
        match self._measurement_code:
            case "SO2":
                return SensorDeviceClass.SULPHUR_DIOXIDE
            case "NO2":
                return SensorDeviceClass.NITROGEN_DIOXIDE
            case "CO":
                return SensorDeviceClass.CO
            case "PM10":
                return SensorDeviceClass.PM10
            case "O3":
                return SensorDeviceClass.OZONE
            case "PM2_5":
                return SensorDeviceClass.PM25
        return None

    @property
    def name(self) -> str:
        """Returns entity name."""
        return self._measurement_name

    @property
    def native_unit_of_measurement(self):
        return "µg/m³"

    @property
    def extra_state_attributes(self) -> dict | None:
        """Returns additional attributes."""
        measurements = self._aq_station.measurements
        if self._measurement_index < len(measurements):
            measurement = measurements[self._measurement_index]
            if not measurement.get("available"):
                return {"info": "Veličina není momentálně k dispozici"}
        return None

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        self._aq_station.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        self._aq_station.remove_callback(self.async_write_ha_state)


class StationSensor(SensorEntity):
    """Sensor for station name."""
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, aq_station):
        self._aq_station = aq_station
        self._attr_unique_id = f"{self._aq_station.station_code}_station"

    @property
    def device_info(self):
        """Returns information to link this entity with the correct device."""
        return self._aq_station.device_info

    @property
    def name(self) -> str:
        """Returns entity name."""
        return "AQ Station"

    @property
    def native_value(self):
        return self._aq_station.name

    @property
    def extra_state_attributes(self):
        return {
            "station_code": self._aq_station.station_code,
            "region": self._aq_station.region,
            "classification": self._aq_station.classification,
            "owner": self._aq_station.owner,
        }

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        self._aq_station.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        self._aq_station.remove_callback(self.async_write_ha_state)


class UpdateSensor(SensorEntity):
    """Sensor for data update."""
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = ICON_UPDATE
    _attr_should_poll = True

    def __init__(self, aq_station):
        self._aq_station = aq_station
        self._attr_unique_id = f"{self._aq_station.station_code}_updated"

    @property
    def device_info(self):
        """Returns information to link this entity with the correct device."""
        return self._aq_station.device_info

    @property
    def name(self) -> str:
        """Returns entity name."""
        return "Data updated"

    @property
    def native_value(self):
        return self._aq_station.data_updated

    async def async_update(self):
        """Calls regular update of data."""
        await self._aq_station.async_update()

