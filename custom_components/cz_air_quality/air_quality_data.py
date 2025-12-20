import aiohttp
import logging
import re

_LOGGER = logging.getLogger(__name__)

API_URL = "https://data-provider.chmi.cz/api/data/tab/ovzdusi.stanice.kvalita.grouped"


class CHMUAirQuality:

    @staticmethod
    async def _fetch_data(search_text="", page_size=300):
        """Internal method to fetch data from CHMI API using POST request.

        Args:
            search_text: Text to search in station names (default "" for all)
            page_size: Number of records to fetch (default 300 to get all stations)

        Returns:
            dict: API response containing header and data
        """
        payload = {
            "filter": None,
            "sort": None,
            "columns": [],
            "paging": {"start": 1, "size": page_size},
            "search": {"columns": ["station_name"], "text": search_text}
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Error fetching data from CHMI API: {e}")
            raise

    @staticmethod
    def _clean_html(html_text):
        """Remove HTML tags from text.

        Args:
            html_text: Text with HTML tags

        Returns:
            str: Clean text without HTML tags
        """
        if not html_text:
            return None
        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', str(html_text))
        return clean.strip()

    @staticmethod
    def _extract_numeric_value(value_text):
        """Extract numeric value from formatted text.

        Args:
            value_text: Text like "<div>13,2 &micro;g∙m<sup>-3</sup></div>"

        Returns:
            float: Numeric value or None
        """
        if not value_text:
            return None
        # Clean HTML and extract number
        clean = CHMUAirQuality._clean_html(value_text)
        if clean:
            # Extract first number (replace comma with dot)
            match = re.search(r'[\d,.]+', clean)
            if match:
                try:
                    return float(match.group().replace(',', '.'))
                except ValueError:
                    return None
        return None

    @staticmethod
    def _process_station_data(station_data):
        """Process raw station data from API.

        Args:
            station_data: Raw station data from API

        Returns:
            dict: Processed and cleaned station data
        """
        return {
            'station_code': station_data.get('station_code'),
            'station_name': CHMUAirQuality._clean_html(station_data.get('station_name')),
            'region': station_data.get('region'),
            'classification': station_data.get('classification'),
            'owner': station_data.get('owner'),
            'air_quality_index': CHMUAirQuality._clean_html(station_data.get('air_quality_index')),
            'datetime': station_data.get('datetime'),
            # Extract numeric values from pollutants
            'so2_1h': CHMUAirQuality._extract_numeric_value(station_data.get('so2_1h')),
            'no2_1h': CHMUAirQuality._extract_numeric_value(station_data.get('no2_1h')),
            'co_8h': CHMUAirQuality._extract_numeric_value(station_data.get('co_8h')),
            'pm10_1h': CHMUAirQuality._extract_numeric_value(station_data.get('pm10_1h')),
            'pm10_24h': CHMUAirQuality._extract_numeric_value(station_data.get('pm10_24h')),
            'pm25_1h': CHMUAirQuality._extract_numeric_value(station_data.get('pm25_1h')),
            'o3_1h': CHMUAirQuality._extract_numeric_value(station_data.get('o3_1h')),
            # Color indicators for limit violations
            'limitPassedColor_aqi': station_data.get('limitPassedColor_aqi'),
        }

    @staticmethod
    async def get_all_station_codes():
        """Get list of all available station codes.

        Returns:
            list: List of station codes (e.g., ['ABRE', 'AHOL', 'ACHO', ...])
        """
        try:
            data = await CHMUAirQuality._fetch_data()
            return [station.get('station_code') for station in data.get("data", []) if station.get('station_code')]
        except Exception as e:
            _LOGGER.error(f"Error getting all station codes: {e}")
            return []

    @staticmethod
    async def get_station_data(station_name):
        """Get data for a specific station by its name (can be partial match).

        Args:
            station_name: Station name or partial name to search for

        Returns:
            dict: Dictionary with 'updated' timestamp and 'station_data' dict, or None if not found
        """
        try:
            # Search for station by name
            data = await CHMUAirQuality._fetch_data(search_text=station_name, page_size=10)

            if not data.get("data"):
                _LOGGER.warning(f"No station found matching: {station_name}")
                return {"updated": None, "station_data": None}

            # Get first matching station
            station_data = data["data"][0]
            processed_data = CHMUAirQuality._process_station_data(station_data)

            return {
                "updated": station_data.get('datetime'),
                "station_data": processed_data
            }
        except Exception as e:
            _LOGGER.error(f"Error getting station data for '{station_name}': {e}")
            return {"updated": None, "station_data": None}
