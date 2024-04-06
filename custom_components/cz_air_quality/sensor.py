"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from datetime import timedelta

from .const import DOMAIN, ICON_UPDATE
from homeassistant.const import EntityCategory, STATE_UNKNOWN, STATE_UNAVAILABLE


SCAN_INTERVAL = timedelta(seconds=900)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    air_quality_station = hass.data[DOMAIN][config_entry.entry_id]
    new_entities = []

    # Set entities for air quality and measurements
    new_entities.append(AirQualitySensor(air_quality_station))
    for i in range(len(air_quality_station.measuments)):
        new_entities.append(MeasurementSensor(i, air_quality_station))

    # Set diagnostic entities
    new_entities.append(StationSensor(air_quality_station))
    new_entities.append(UpdateSensor(air_quality_station))

    # Add all entities to HA
    async_add_entities(new_entities)


class AirQualitySensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, aq_station):

        self._aq_station = aq_station
        self._attr_unique_id = f"{self._aq_station.name}_aqi"

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
        return f"AQ Index {self._aq_station.name}"

    @property
    def device_class(self) -> str:
        """Returns device class"""
        return SensorDeviceClass.AQI

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._aq_station.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._aq_station.remove_callback(self.async_write_ha_state)


class MeasurementSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, measurement: int, aq_station):

        self._measurement = measurement
        self._aq_station = aq_station
        self._attr_unique_id = f"{self._aq_station.name}_{self._measurement}"

    @property
    def device_info(self) -> str:
        """Return information to link this entity with the correct device."""
        return self._aq_station.device_info

    @property
    def native_value(self) -> str:
        """ Returns data as state if available."""
        if self._aq_station.measurements[self._measurement]["Flag"] == "no_meas":
            return STATE_UNAVAILABLE
        elif self._aq_station.measurements[self._measurement]["Flag"] == "no_data":
            return STATE_UNKNOWN
        elif self._aq_station.measurements[self._measurement]["Flag"] == "ok":
            if self._aq_station.measurements[self._measurement]["Val"] != "":
                return STATE_UNKNOWN
            else:
                return self._aq_station.measurements[self._measurement]["Val"]

    @property
    def name(self) -> str:
        """Returns entity name"""
        return self._aq_station.measurements[self._measurement]["Code"]

    @property
    def device_class(self) -> str:
        """Returns device class"""
        match self._aq_station.measurements[self._measurement]["Code"]:
            case "SO2":
                return SensorDeviceClass.SULPHUR_DIOXIDE
            case "NO2":
                return SensorDeviceClass.NITROGEN_DIOXIDE
            case "PM10" | "PM10_Model":
                return SensorDeviceClass.PM10
            case "O3" | "O3_Model":
                return SensorDeviceClass.OZONE
            case "PM2_5":
                return SensorDeviceClass.PM25

    @property
    def native_unit_of_measurement(self):
        return "µg/m³"

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._aq_station.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._aq_station.remove_callback(self.async_write_ha_state)


class StationSensor(SensorEntity):
    """Sensor for station name."""
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, aq_station):

        self._aq_station = aq_station
        self._attr_unique_id = f"{self._aq_station.name}_station"

    @property
    def device_info(self):
        """Returns information to link this entity with the correct device."""
        return self._aq_station.device_info

    @property
    def name(self) -> str:
        """Returns entity name"""
        return "AQ Station"

    @property
    def native_value(self):
        return self._aq_station.name

    @property
    def extra_state_attributes(self):
        return {"latitude": self._aq_station.latitude, "longitude": self._aq_station.longitude}


class UpdateSensor(SensorEntity):
    """Sensor for data update."""
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = ICON_UPDATE
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, aq_station):

        self._aq_station = aq_station
        self._attr_unique_id = f"{self._aq_station.name}_updated"

    @property
    def device_info(self):
        """Returns information to link this entity with the correct device."""
        return self._aq_station.device_info

    @property
    def name(self) -> str:
        """Returns entity name"""
        return "Data updated"

    @property
    def native_value(self):
        return self._aq_station.updated

    async def async_update(self):
        """ Calls regular update of data . """
        await self._aq_station.async_update()

