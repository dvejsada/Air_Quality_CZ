"""Shared test data for the CHMU Air Quality integration."""
from __future__ import annotations

API_URL = "https://data-provider.chmi.cz/api/data/tab/ovzdusi.stanice.kvalita.grouped"

UPDATED = "2026-06-28T12:00:00.000Z"
# Expected ISO representation after parsing into a tz-aware datetime.
UPDATED_ISO = "2026-06-28T12:00:00+00:00"


def _name(slug: str, label: str) -> str:
    """Build an HTML-wrapped station name as returned by the API."""
    return f'<a data-senna-off="true" href="/{slug}">{label}</a>'


def _value(text: str) -> str:
    """Build an HTML-wrapped measurement value as returned by the API."""
    return f"<div>{text} &micro;g∙m<sup>-3</sup></div>"


def _index(value: str) -> str:
    """Build an HTML-wrapped air quality index value."""
    return f"<div style='text-align: center;'>{value}</div>"


# A representative sample of the CHMI API response (a handful of stations,
# including two whose names share a common prefix to exercise exact matching).
SAMPLE_API_RESPONSE = {
    "header": {"paging": {"start": 1, "size": 300}, "totalCount": 4},
    "data": [
        {
            "datetime": UPDATED,
            "state": "CZ",
            "station_code": "ABRE",
            "station_name": _name("abre", "Praha 6-Břevnov"),
            "classification": "B/U/RN",
            "region": "Praha",
            "owner": "Český hydrometeorologický ústav",
            "air_quality_index": _index("2B"),
            "so2_1h": None,
            "no2_1h": _value("7,3"),
            "co_8h": None,
            "pm10_1h": _value("18,6"),
            "pm10_24h": _value("25,6"),
            "pm25_1h": None,
            "o3_1h": None,
            "limitPassedColor_aqi": "#FAA61A",
        },
        {
            "datetime": UPDATED,
            "state": "CZ",
            "station_code": "BBMD",
            "station_name": _name("bbmd", "Brno-Dětská nemocnice"),
            "classification": "B/U/R",
            "region": "Jihomoravský",
            "owner": "Český hydrometeorologický ústav",
            "air_quality_index": _index("1A"),
            "so2_1h": _value("1,1"),
            "no2_1h": _value("4,4"),
            "co_8h": _value("210,0"),
            "pm10_1h": _value("12,0"),
            "pm10_24h": _value("26,0"),
            "pm25_1h": _value("2,2"),
            "o3_1h": _value("132,1"),
            "limitPassedColor_aqi": "#009900",
        },
        {
            "datetime": UPDATED,
            "state": "CZ",
            "station_code": "SKLS",
            "station_name": _name("skls", "Kladno"),
            "classification": "B/U/R",
            "region": "Středočeský",
            "owner": "Český hydrometeorologický ústav",
            "air_quality_index": _index("1B"),
            "so2_1h": None,
            "no2_1h": _value("5,0"),
            "co_8h": None,
            "pm10_1h": _value("10,0"),
            "pm10_24h": _value("11,0"),
            "pm25_1h": None,
            "o3_1h": None,
            "limitPassedColor_aqi": "#00CC00",
        },
        {
            "datetime": UPDATED,
            "state": "CZ",
            "station_code": "SKLM",
            "station_name": _name("sklm", "Kladno-Švermov"),
            "classification": "B/S/R",
            "region": "Středočeský",
            "owner": "Český hydrometeorologický ústav",
            "air_quality_index": _index("0"),
            "so2_1h": None,
            "no2_1h": None,
            "co_8h": None,
            "pm10_1h": None,
            "pm10_24h": None,
            "pm25_1h": None,
            "o3_1h": None,
            "limitPassedColor_aqi": "#FFFFFF",
        },
    ],
}

# Station name used as the primary fixture across the HA integration tests.
STATION_NAME = "Praha 6-Břevnov"
STATION_CODE = "ABRE"


def mock_api(aioclient_mock, response: dict | None = None) -> None:
    """Register the CHMI POST endpoint with an HA aioclient mock."""
    aioclient_mock.post(
        API_URL,
        json=SAMPLE_API_RESPONSE if response is None else response,
    )
