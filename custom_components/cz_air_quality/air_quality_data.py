import requests
import logging

_LOGGER = logging.getLogger(__name__)

URL = "https://www.chmi.cz/files/portal/docs/uoco/web_generator/aqindex_3h_cze.json"


class CHMUAirQuality:

    @staticmethod
    def update_info(station):
        """ Gets new data from website"""
        response = requests.get(URL)
        res = response.json()
        data = CHMUAirQuality.parse_data(res, station)
        return data

    @staticmethod
    def parse_data(data, station) -> dict:
        """Returns data for relevant station"""
        res = None
        for i in range(len(data["States"][0]['Regions'])):
            for sub in data["States"][0]['Regions'][i]["Stations"]:
                if sub['Name'] == station:
                    res = sub
                    break
            if res is not None:
                break

        return {"updated": data["Actualized"], "station_data": res}
