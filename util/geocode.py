import requests
import urllib
from geopy.geocoders import Nominatim
import os

key = os.environ.get('GOOGLE_MAPS_API_KEY')

def get_lat_long(address, report):
    lat, lng = None, None
    param = {
        "address": address,
        "key": key
    }
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    endpoint = f"{base_url}{urllib.parse.urlencode(param)}"
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        print("oops")
        return address, 0, 0
    try:
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
        address = results['formatted_address']
    except:
        pass
    return address, lat, lng