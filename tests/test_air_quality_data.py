"""Unit tests for the CHMI API client and its parsing helpers.

These tests do not depend on Home Assistant and exercise the pure parsing
logic plus the HTTP methods (with aiohttp mocked via aioresponses).
"""
from __future__ import annotations

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.cz_air_quality.air_quality_data import (
    API_URL,
    CHMUAirQuality,
    CHMUApiError,
)

from .const import SAMPLE_API_RESPONSE


def test_clean_html() -> None:
    """HTML tags are stripped and empty values become None."""
    assert CHMUAirQuality._clean_html("<div>2B</div>") == "2B"
    assert (
        CHMUAirQuality._clean_html('<a href="/x">Praha 6-Břevnov</a>')
        == "Praha 6-Břevnov"
    )
    assert CHMUAirQuality._clean_html(None) is None
    assert CHMUAirQuality._clean_html("") is None
    assert CHMUAirQuality._clean_html("<div></div>") is None


def test_extract_numeric_value() -> None:
    """Numeric values are parsed from formatted strings (comma decimals)."""
    assert CHMUAirQuality._extract_numeric_value(
        "<div>13,2 &micro;g∙m<sup>-3</sup></div>"
    ) == 13.2
    assert CHMUAirQuality._extract_numeric_value("<div>210,0</div>") == 210.0
    assert CHMUAirQuality._extract_numeric_value(None) is None
    assert CHMUAirQuality._extract_numeric_value("<div>n/a</div>") is None


def test_process_station_data() -> None:
    """Raw records are normalised into clean dictionaries."""
    processed = CHMUAirQuality._process_station_data(
        SAMPLE_API_RESPONSE["data"][0]
    )
    assert processed["station_code"] == "ABRE"
    assert processed["station_name"] == "Praha 6-Břevnov"
    assert processed["air_quality_index"] == "2B"
    assert processed["no2_1h"] == 7.3
    assert processed["pm10_24h"] == 25.6
    assert processed["so2_1h"] is None


async def test_get_all_station_names() -> None:
    """All station names are returned, cleaned of HTML."""
    with aioresponses() as mocked:
        mocked.post(API_URL, payload=SAMPLE_API_RESPONSE)
        async with aiohttp.ClientSession() as session:
            names = await CHMUAirQuality(session).get_all_station_names()
    assert names == [
        "Praha 6-Břevnov",
        "Brno-Dětská nemocnice",
        "Kladno",
        "Kladno-Švermov",
    ]


async def test_get_station_data_exact_match() -> None:
    """An exact name match wins even when the search returns several rows."""
    with aioresponses() as mocked:
        mocked.post(API_URL, payload=SAMPLE_API_RESPONSE)
        async with aiohttp.ClientSession() as session:
            result = await CHMUAirQuality(session).get_station_data("Kladno")
    assert result["station_data"]["station_code"] == "SKLS"
    assert result["station_data"]["station_name"] == "Kladno"
    assert result["updated"] == "2026-06-28T12:00:00.000Z"


async def test_get_station_data_not_found() -> None:
    """An empty result set yields a None station payload."""
    with aioresponses() as mocked:
        mocked.post(API_URL, payload={"header": {}, "data": []})
        async with aiohttp.ClientSession() as session:
            result = await CHMUAirQuality(session).get_station_data("Nowhere")
    assert result == {"updated": None, "station_data": None}


async def test_get_station_data_raises_on_http_error() -> None:
    """Network/HTTP failures are surfaced as CHMUApiError."""
    with aioresponses() as mocked:
        mocked.post(API_URL, status=500)
        async with aiohttp.ClientSession() as session:
            with pytest.raises(CHMUApiError):
                await CHMUAirQuality(session).get_station_data("Praha")
