# Czech Republic Air Quality Measurements

This custom component provides a air quality measurements provides by Czech Hydro-meteorological Institute [CHMU](http://www.chmi.cz/?tab=2/). 

Multiple air quality stations may be configured.

## Installation

### Using [HACS](https://hacs.xyz/)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dvejsada&repository=Air_Quality_CZ&category=Integration)

### Manual

To install this integration manually you have to download cz_air_quality folder into your config/custom_components folder.

## Configuration

### Using UI

From the Home Assistant front page go to **Configuration** and then select **Integrations** from the list.

Use the "plus" button in the bottom right to add a new integration called **CHMU Air Quality** and choose preferred air quality station.

You can find the closest air quality station [here](http://pr-asu.chmi.cz:8080/IskoOzarkApp/rest/map_3h_cz/)

The success dialog will appear or an error will be displayed in the popup. Please note that not all stations measure all pollutants - some entities thus may be unavailable.
