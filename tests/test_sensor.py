"""Tests for the CHMU Air Quality sensor platform."""
from __future__ import annotations

from homeassistant.components.sensor import ATTR_STATE_CLASS, SensorStateClass
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cz_air_quality.const import DOMAIN

from .const import STATION_CODE, UPDATED_ISO, mock_api


def _entity_id(hass: HomeAssistant, unique_suffix: str) -> str:
    """Return the entity_id for a sensor by its unique_id suffix."""
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{STATION_CODE}_{unique_suffix}"
    )
    assert entity_id is not None, f"missing entity for {unique_suffix}"
    return entity_id


async def _setup(hass, aioclient_mock, entry) -> None:
    mock_api(aioclient_mock)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_entities_created(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """All expected entities are registered for the station."""
    await _setup(hass, aioclient_mock, mock_config_entry)

    entities = er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )
    # 3 fixed sensors (aqi, station, updated) + 7 measurements.
    assert len(entities) == 10


async def test_air_quality_index_sensor(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """The AQI sensor reports the index and its descriptive attributes."""
    await _setup(hass, aioclient_mock, mock_config_entry)

    state = hass.states.get(_entity_id(hass, "aqi"))
    assert state.state == "2B"
    assert state.attributes["description"] == "přijatelná"
    assert state.attributes["color"] == "FAA61A"


async def test_measurement_sensor(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """A pollutant sensor reports its value, unit and state class."""
    await _setup(hass, aioclient_mock, mock_config_entry)

    state = hass.states.get(_entity_id(hass, "no2_1h"))
    assert state.state == "7.3"
    assert (
        state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        == CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    )
    assert state.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT
    assert state.attributes[ATTR_DEVICE_CLASS] == "nitrogen_dioxide"


async def test_unavailable_measurement_is_unknown(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """A pollutant not measured by the station reports as unknown."""
    await _setup(hass, aioclient_mock, mock_config_entry)

    # SO2 is null for the configured station.
    state = hass.states.get(_entity_id(hass, "so2_1h"))
    assert state.state == "unknown"


async def test_data_updated_timestamp(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """The data-updated sensor exposes a parsed timestamp."""
    await _setup(hass, aioclient_mock, mock_config_entry)

    state = hass.states.get(_entity_id(hass, "updated"))
    assert state.state == UPDATED_ISO
    assert state.attributes[ATTR_DEVICE_CLASS] == "timestamp"


async def test_station_sensor_attributes(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """The diagnostic station sensor exposes station metadata."""
    await _setup(hass, aioclient_mock, mock_config_entry)

    state = hass.states.get(_entity_id(hass, "station"))
    assert state.state == "Praha 6-Břevnov"
    assert state.attributes["station_code"] == STATION_CODE
    assert state.attributes["region"] == "Praha"
