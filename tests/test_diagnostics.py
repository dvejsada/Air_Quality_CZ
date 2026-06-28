"""Tests for the CHMU Air Quality diagnostics."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cz_air_quality.diagnostics import (
    async_get_config_entry_diagnostics,
)

from .const import STATION_CODE, mock_api


async def test_config_entry_diagnostics(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """Diagnostics include entry data and the last coordinator payload."""
    mock_api(aioclient_mock)
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    assert diagnostics["last_update_success"] is True
    assert diagnostics["data"]["station_data"]["station_code"] == STATION_CODE
