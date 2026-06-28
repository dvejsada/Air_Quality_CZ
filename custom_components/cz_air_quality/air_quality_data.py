"""Client for the CHMI (Czech Hydrometeorological Institute) air quality API."""
from __future__ import annotations

import logging
import re

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_URL = "https://data-provider.chmi.cz/api/data/tab/ovzdusi.stanice.kvalita.grouped"
REQUEST_TIMEOUT = 30

# Keys of the pollutant measurements returned by the API.
MEASUREMENT_KEYS = (
    "so2_1h",
    "no2_1h",
    "co_8h",
    "pm10_1h",
    "pm10_24h",
    "pm25_1h",
    "o3_1h",
)


class CHMUApiError(Exception):
    """Raised when communication with the CHMI API fails."""


class CHMUAirQuality:
    """Asynchronous client for the CHMI air quality API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialise the client with a shared aiohttp session."""
        self._session = session

    async def _fetch_data(self, search_text: str = "", page_size: int = 300) -> dict:
        """Fetch data from the CHMI API using a POST request.

        Args:
            search_text: Text to search in station names ("" returns all).
            page_size: Number of records to fetch.

        Returns:
            The decoded JSON payload containing ``header`` and ``data``.

        Raises:
            CHMUApiError: If the request fails or returns invalid data.
        """
        payload = {
            "filter": None,
            "sort": None,
            "columns": [],
            "paging": {"start": 1, "size": page_size},
            "search": {"columns": ["station_name"], "text": search_text},
        }

        try:
            async with self._session.post(
                API_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            raise CHMUApiError(f"Error fetching data from CHMI API: {err}") from err

    @staticmethod
    def _clean_html(html_text) -> str | None:
        """Strip HTML tags from a value returned by the API."""
        if not html_text:
            return None
        clean = re.sub("<[^<]+?>", "", str(html_text))
        return clean.strip() or None

    @staticmethod
    def _extract_numeric_value(value_text) -> float | None:
        """Extract the numeric value from a formatted measurement string.

        Example input: ``"<div>13,2 &micro;g∙m<sup>-3</sup></div>"``.
        """
        clean = CHMUAirQuality._clean_html(value_text)
        if not clean:
            return None
        match = re.search(r"[\d,.]+", clean)
        if not match:
            return None
        try:
            return float(match.group().replace(",", "."))
        except ValueError:
            return None

    @staticmethod
    def _process_station_data(station_data: dict) -> dict:
        """Normalise a raw station record into a clean dictionary."""
        processed = {
            "station_code": station_data.get("station_code"),
            "station_name": CHMUAirQuality._clean_html(station_data.get("station_name")),
            "region": station_data.get("region"),
            "classification": station_data.get("classification"),
            "owner": station_data.get("owner"),
            "air_quality_index": CHMUAirQuality._clean_html(
                station_data.get("air_quality_index")
            ),
            "datetime": station_data.get("datetime"),
            "limitPassedColor_aqi": station_data.get("limitPassedColor_aqi"),
        }
        for key in MEASUREMENT_KEYS:
            processed[key] = CHMUAirQuality._extract_numeric_value(
                station_data.get(key)
            )
        return processed

    async def get_all_station_names(self) -> list[str]:
        """Return the list of all available station names."""
        data = await self._fetch_data()
        names = [
            CHMUAirQuality._clean_html(station.get("station_name"))
            for station in data.get("data", [])
            if station.get("station_name")
        ]
        return [name for name in names if name]

    async def get_station_data(self, station_name: str) -> dict:
        """Return the data for a specific station by (full) name.

        The API search is a substring match that can return several stations,
        so the result is filtered for an exact name match before falling back
        to the first record.

        Returns:
            A dict with an ``updated`` timestamp and a ``station_data`` dict.
            ``station_data`` is ``None`` when no station matches.
        """
        data = await self._fetch_data(search_text=station_name, page_size=20)
        records = data.get("data") or []

        if not records:
            _LOGGER.warning("No station found matching: %s", station_name)
            return {"updated": None, "station_data": None}

        # Prefer an exact name match; fall back to the first record.
        station_data = next(
            (
                record
                for record in records
                if CHMUAirQuality._clean_html(record.get("station_name"))
                == station_name
            ),
            records[0],
        )

        processed_data = CHMUAirQuality._process_station_data(station_data)
        return {
            "updated": station_data.get("datetime"),
            "station_data": processed_data,
        }
