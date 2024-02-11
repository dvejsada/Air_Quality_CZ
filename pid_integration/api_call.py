import requests
import logging
from .const import API_URL
_LOGGER = logging.getLogger(__name__)


class ApiCall:

    @staticmethod
    def update_info(api_key, stop_id, conn_num):
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"aswIds": stop_id, "total": conn_num, "minutesAfter": 10080}

        response = requests.get(API_URL, params=parameters, headers=headers)
        return response.json()

    @staticmethod
    def authenticate(api_key, stop_id, conn_num):
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"aswIds": stop_id, "total": conn_num, "minutesAfter": 10080}
        response = requests.get(API_URL, params=parameters, headers=headers)
        reply = response.json()
        title = reply["stops"][0]["stop_name"] + " " + ApiCall.check_not_null(reply["stops"][0]["platform_code"])
        if response.status_code == 200:
            return True, title
        else:
            return False, None

    @staticmethod
    def check_not_null(response):
        if response is not None:
            value = response
        else:
            value = ""
        return value

