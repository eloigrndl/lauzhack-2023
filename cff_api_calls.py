'''
   API calls to CFF & open-route-services
'''

import os
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from utils import format_json, haversine_formula, get_token

# Load the .env file
load_dotenv()

# Access variables
JOURNEY_API_URL = os.getenv("JOURNEY_API_URL")
DATA_API_URL = os.getenv("DATA_API_URL")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
SCOPE = os.getenv("SCOPE")
ORS_API_KEY = os.getenv("OPEN_ROUTE_API_KEY")
ORS_API_URL = os.getenv("OPEN_ROUTE_API_URL")

# Max distance to search for P+Rs
MAX_PR_DISTANCE = 5.0
NUM_CLOSEST_PRS = 5

TRAFFIC_FACTOR = 1.1


def get_places_by_geoloc(longitude: float, latitude: float):
    '''
        Get places by geoloc
    '''

    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'accept': 'application/json; charset=utf-8',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }

    params = {
        'longitude': longitude,
        'latitude': latitude,
        'radius': '400',
        'limit': '10',
        'type': 'StopPlace'
    }

    response = requests.get(
        JOURNEY_API_URL + "/v3/places/by-coordinates",
        headers=headers, params=params, timeout=0.5
    )
    print(response.json())
    return response.json()


def get_places_by_name(name, limit=10):
    '''
        Get places by name
    '''
    token = get_token()

    headers = {
        'Authorization': f"Bearer {token}"
    }

    params = {
        'nameMatch': name,
        'limit': limit
    }
    response = requests.get(
        JOURNEY_API_URL + "/v3/places",
        headers=headers, params=params, timeout=0.5
    )
    return response.json()


def get_time_only_car(origin: [float], dest: [float]) -> (datetime, float, float):
    '''
        Call Open Route Service to get the route between origin and dest
        coordinates = [longitude, latitude]
    '''

    headers = {
        'Authorization': ORS_API_KEY,
        'accept': 'application/json; charset=utf-8',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    body = {'coordinates': [origin, dest]}

    response = requests.post(
        ORS_API_URL + "/v2/directions/driving-car", headers=headers, json=body, timeout=0.5)

    routes = response.json()['routes']
    if len(routes) < 1:
        print("No routes found between provided geopoints")
        return None, None, None

    itinerary = routes[0]
    distance = round(itinerary['summary']['distance'], 2)
    duration = round(itinerary['summary']['duration'] * TRAFFIC_FACTOR, 2)
    eta = datetime.now() + timedelta(seconds=duration)

    return eta, duration, distance


def get_trip_by_origin_and_destination(
    origin,
    destination,
    date=datetime.today().strftime('%Y-%m-%d'),
    time=datetime.now().strftime('%H:%M')
):
    '''
        This function returns the trip from origin to destination.
    '''

    path = '/v3/trips/by-origin-destination'
    token = get_token()
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
    }
    data = {
        'origin': origin,
        'destination': destination,
        'date': date,
        'time': time,
        'includeEcologyComparison': 'DEFAULT'
    }
    trips = requests.post(JOURNEY_API_URL + path,
                          headers=headers, json=data, timeout=2)
    return trips.json()


def get_closest_PRs(geoloc, max_dist=MAX_PR_DISTANCE, num_closest=NUM_CLOSEST_PRS):
    '''
        Get the closest P+Rs given a geolocation and a maximum distance
        geoloc : [longitude, latitude]
    '''
    with open('data/mobilitat.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        # Extract coordinates of the target geolocation
        target_lat, target_lon = geoloc[1], geoloc[0]

        # Calculate distances and store them in a list of tuples (location, distance)
        distances = []
        for entry in dataset:
            distance = haversine_formula(
                target_lat, target_lon, entry['geopos']['lat'], entry['geopos']['lon'])

            if distance <= float(max_dist) and entry['parkrail_anzahl'] is not None and entry['parkrail_anzahl'] > 0:
                print(entry['parkrail_anzahl'])
                distances.append([entry, distance])

        # Sort the locations by distance
        sorted_locations = sorted(distances, key=lambda x: x[1])

        # Get the closest locations (first num_closest elements)
        closest_locations = sorted_locations[:num_closest]

    return closest_locations


def get_closest_PRs_with_new_dataset(geoloc, max_dist=MAX_PR_DISTANCE, num_closest=NUM_CLOSEST_PRS):
    '''
        Get the closest P+Rs given a geolocation and a maximum distance
        geoloc : [longitude, latitude]
    '''
    with open('data/parking-facilities.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        # Extract coordinates of the target geolocation
        target_lat, target_lon = geoloc[1], geoloc[0]

        # Calculate distances and store them in a list of tuples (location, distance)
        distances = []
        for entry in dataset['features']:
            distance = haversine_formula(
                target_lat, target_lon, entry['geometry']['coordinates'][1], entry['geometry']['coordinates'][0])

            if distance <= float(max_dist):
                distances.append([entry, distance])

        # Sort the locations by distance
        sorted_locations = sorted(distances, key=lambda x: x[1])

        # Get the closest locations (first num_closest elements)
        closest_locations = sorted_locations[:num_closest]

    return closest_locations


# if __name__ == "__main__":
    # placeLausanne = get_places_by_name("EPFL")["places"][0]
    # print(format_json(get_closest_PRs(
    #     placeLausanne["centroid"]["coordinates"])))

    # eta, duration, distance = time_get_only_car(
    #     [8.681495, 49.41461], [8.686507, 49.41943])
    # formatted_datetime = eta.strftime("%Y-%m-%d %H:%M:%S")
    # print(formatted_datetime, distance, duration)
    # print("Do stuff")

    # epfl_places = get_places_by_name("EPFL", 1)
    # lausanne_places = get_places_by_name("Lausanne", 1)
    # if 'places' in epfl_places and 'places' in lausanne_places:
    #     trips = get_trip_by_origin_and_destination(
    #         epfl_places['places'][0]['id'],
    #         lausanne_places['places'][0]['id']
    #     )
    #     if 'trips' in trips:
    #         print(f"The engine found {len(trips['trips'])} trips from "
    #               + f"'{epfl_places['places'][0]['name']}' to '{lausanne_places['places'][0]['name']}'.")
    # else:
    #     print("Did not find places.")

    # get_places_by_geoloc(6.140324, 46.243203)
