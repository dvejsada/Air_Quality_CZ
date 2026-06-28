# Czech Republic Air Quality Measurements

This custom component provides air quality measurements provided by the Czech Hydrometeorological Institute [CHMU](http://www.chmi.cz/?tab=2/).

Multiple air quality stations may be configured. For each station the integration creates:

- an **air quality index** sensor (enum with colour/recommendation attributes),
- a **measurement** sensor per pollutant (SO₂, NO₂, CO, PM10 1h/24h, PM2.5, O₃) with long-term statistics enabled,
- a diagnostic **station** sensor (code, region, classification, owner),
- a diagnostic **data updated** timestamp sensor.

Data is refreshed once per hour using a `DataUpdateCoordinator` and Home Assistant's shared HTTP session.

## Installation

### Using [HACS](https://hacs.xyz/)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dvejsada&repository=Air_Quality_CZ&category=Integration)

### Manual

To install this integration manually you have to download cz_air_quality folder into your config/custom_components folder.

## Configuration

### Using UI

From the Home Assistant front page go to **Configuration** and then select **Integrations** from the list.

Use the "plus" button in the bottom right to add a new integration called **CHMU Air Quality** and choose the preferred air quality station from the dropdown list (stations are loaded directly from CHMI).

You can find the closest air quality station on the [CHMI air quality map](https://www.chmi.cz/files/portal/docs/uoco/web_generator/aktual_hod_data_CZ.html).

The success dialog will appear or an error will be displayed in the popup. Please note that not all stations measure all pollutants - some entities may therefore report as unknown.
