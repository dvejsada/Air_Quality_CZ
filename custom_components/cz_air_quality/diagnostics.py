"""Diagnostics support for the CHMU Air Quality integration."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .coordinator import CHMUConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: CHMUConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "entry": {
            "title": entry.title,
            "data": dict(entry.data),
        },
        "last_update_success": coordinator.last_update_success,
        "data": coordinator.data,
    }
