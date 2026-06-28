"""Tests for setup and unload of the CHMU Air Quality integration."""
from __future__ import annotations

import aiohttp

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cz_air_quality.const import CONF_STOP_SEL, DOMAIN

from .const import STATION_NAME, mock_api


async def test_setup_and_unload(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """A config entry sets up and unloads cleanly."""
    mock_api(aioclient_mock)
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_config_entry.runtime_data is not None

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_retry_on_api_error(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """A failing first refresh puts the entry into the retry state."""
    aioclient_mock.post(
        "https://data-provider.chmi.cz/api/data/tab/ovzdusi.stanice.kvalita.grouped",
        exc=aiohttp.ClientError(),
    )
    mock_config_entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_options_update_reloads_entry(
    hass: HomeAssistant, aioclient_mock, mock_config_entry: MockConfigEntry
) -> None:
    """Updating options reloads the entry with the new scan interval."""
    mock_api(aioclient_mock)
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_SCAN_INTERVAL: 45}
    )
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    coordinator = mock_config_entry.runtime_data
    assert coordinator.update_interval.total_seconds() == 45 * 60
