"""Fixtures for the CHMU Air Quality tests."""
from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cz_air_quality.const import CONF_STOP_SEL, DOMAIN

from .const import STATION_NAME


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of the custom integration in every test."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry for the default station."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=STATION_NAME,
        unique_id=STATION_NAME,
        data={CONF_STOP_SEL: STATION_NAME},
    )
