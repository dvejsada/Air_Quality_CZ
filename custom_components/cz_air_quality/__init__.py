"""The CHMU Air Quality integration."""
from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_STOP_SEL
from .coordinator import CHMUConfigEntry, CHMUDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: CHMUConfigEntry) -> bool:
    """Set up an air quality station from a config entry."""
    coordinator = CHMUDataUpdateCoordinator(hass, entry, entry.data[CONF_STOP_SEL])
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: CHMUConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
