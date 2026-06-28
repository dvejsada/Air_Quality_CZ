"""Constants for the CHMU Air Quality integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass

DOMAIN = "cz_air_quality"

# Config entry keys (kept stable for backwards compatibility with existing entries).
CONF_STOP_SEL = "station_selector"

ICON_UPDATE = "mdi:update"

MANUFACTURER = "Czech Hydrometeorological Institute"

DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

# Definition of pollutant measurements exposed as sensors.
# ``device_class`` is omitted where the CHMI unit (µg/m³) is incompatible with
# the Home Assistant device class (e.g. CO expects ppm).
MEASUREMENT_DEFINITIONS: list[dict] = [
    {"key": "so2_1h", "name": "SO2", "device_class": SensorDeviceClass.SULPHUR_DIOXIDE},
    {"key": "no2_1h", "name": "NO2", "device_class": SensorDeviceClass.NITROGEN_DIOXIDE},
    {"key": "co_8h", "name": "CO", "device_class": None},
    {"key": "pm10_1h", "name": "PM10 1h", "device_class": SensorDeviceClass.PM10},
    {"key": "pm10_24h", "name": "PM10 24h", "device_class": SensorDeviceClass.PM10},
    {"key": "pm25_1h", "name": "PM2.5", "device_class": SensorDeviceClass.PM25},
    {"key": "o3_1h", "name": "O3", "device_class": SensorDeviceClass.OZONE},
]

# Possible values of the air quality index (used as ENUM sensor options).
AQI_OPTIONS = ["1A", "1B", "2A", "2B", "3A", "3B", "0", "-1"]

# Static metadata (colour and description/recommendation) for each index value.
AQI_ATTRIBUTES: dict[str, dict[str, str]] = {
    "1A": {
        "color": "009900",
        "color_text": "000000",
        "description": "velmi dobrá",
        "recommendation": "Ideální podmínky pro pobyt venku",
    },
    "1B": {
        "color": "00CC00",
        "color_text": "000000",
        "description": "dobrá",
        "recommendation": "Venkovní aktivity bez omezení",
    },
    "2A": {
        "color": "FFF200",
        "color_text": "000000",
        "description": "přijatelná",
        "recommendation": "Venkovní aktivity bez omezení",
    },
    "2B": {
        "color": "FAA61A",
        "color_text": "000000",
        "description": "přijatelná",
        "recommendation": "Není třeba měnit své obvyklé aktivity venku.",
    },
    "3A": {
        "color": "ED1C24",
        "color_text": "FFFFFF",
        "description": "zhoršená",
        "recommendation": (
            "Zvažte snížení nebo odložení/přesunutí namáhavé činnosti venku, "
            "pokud se objeví příznaky, jako je kašel a podráždění krku."
        ),
    },
    "3B": {
        "color": "671F20",
        "color_text": "FFFFFF",
        "description": "špatná",
        "recommendation": (
            "Omezte nebo odložte namáhavé činnosti venku, zvláště když "
            "zaznamenáte jakékoliv nepříjemné pocity a příznaky jako je "
            "dráždění v krku, pálení očí kašel apod."
        ),
    },
    "0": {
        "color": "FFFFFF",
        "color_text": "000000",
        "description": "neúplná data",
    },
    "-1": {
        "color": "CFCFCF",
        "color_text": "000000",
        "description": "index nestanoven",
    },
}
