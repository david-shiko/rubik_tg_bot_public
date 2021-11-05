from postconfig import logger
from config import yandex_api_key
from geopy.geocoders import Yandex  # For location


def get_location_from_coordinates(location):
    try:
        locator = Yandex(api_key=yandex_api_key, timeout=3)  # for location
        location = locator.reverse(f'{location.latitude}, {location.longitude}', exactly_one=True)  # full address str
        return location.address.split()[-2:]  # Only city and country
    except Exception as e:
        logger.error(f'Error in get_location_from_coordinates, {e}')
