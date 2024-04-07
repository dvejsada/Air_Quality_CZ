import requests
import logging

_LOGGER = logging.getLogger(__name__)

URL = "https://www.chmi.cz/files/portal/docs/uoco/web_generator/aqindex_3h_cze.json"


class CHMUAirQuality:

    @staticmethod
    def get_data():
        """ Gets new data from website"""
        response = requests.get(URL)
        data = response.json()
        return data

    @staticmethod
    def update_info(station) -> dict:
        """ Parse data to get specific station."""
        data = CHMUAirQuality.get_data()
        res = None

        # Loops over the station to get data for specific station.
        for i in range(len(data["States"][0]['Regions'])):
            for sub in data["States"][0]['Regions'][i]["Stations"]:
                if sub['Name'] == station:
                    res = sub
                    break
            if res is not None:
                break

        # Return the data for specific station only
        return {"updated": data["Actualized"], "station_data": res}

    @staticmethod
    def validate_station(station):
        """ Validate the station is in the list."""
        data = CHMUAirQuality.get_data()
        for i in range(len(data["States"][0]['Regions'])):
            for sub in data["States"][0]['Regions'][i]["Stations"]:
                if sub['Name'] == station:
                    return None
        return False
