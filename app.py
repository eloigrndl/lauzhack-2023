'''
    Flask server
'''
import os
import json
import ast
from datetime import datetime, timedelta
import isodate
import requests
from dotenv import load_dotenv
from flask import Flask, request, abort
from flask_cors import CORS
from utils import get_token, haversine_formula


# Load the .env file
load_dotenv()

JOURNEY_API_URL = os.getenv("JOURNEY_API_URL")
ORS_API_KEY = os.getenv("OPEN_ROUTE_API_KEY")
ORS_API_URL = os.getenv("OPEN_ROUTE_API_URL")

# Global variables definitions
NUM_PLACE_RESULTS = 10
TRAFFIC_FACTOR = 1.1
MAX_PR_DISTANCE = 5.0
NUM_CLOSEST_PRS = 5

app = Flask(__name__)
CORS(app)

@app.route("/v1/places/by-name", methods=['GET'])
def places_by_name():
    '''
        Get places by name
    '''
    name = request.args.get('name', default="", type=str)
    if name == "":
        abort(400)
    limit = request.args.get('limit', default=10, type=int)

    token = get_token()
    path = "/v3/places"
    headers = {
        'Authorization': f"Bearer {token}"
    }
    params = {
        'nameMatch': name,
        'limit': limit
    }
    response = requests.get(
        JOURNEY_API_URL + path,
        headers=headers, params=params, timeout=2
    )

    places = []
    for place in response.json()["places"]:
        custom_place = {
            "id": place["id"],
            "name": place["name"],
            "geoloc": place["centroid"]["coordinates"],
        }
        places.append(custom_place)

    return places


@app.route("/v1/trips/by-origin-destination", methods=['POST'])
def trips_by_origin_and_destination():
    '''
        This function represent our main engine. It takes as query parameters the origin and the
        destination chosen by the user, and optionnally date and time.
    '''
    origin_object = request.json.get('origin', "")
    dest_object = request.json.get('destination', "")
    if origin_object == "" or dest_object == "":
        abort(400)
    date = request.args.get(
        'date', default=datetime.today().strftime('%Y-%m-%d'), type=str)
    time = request.args.get(
        'time', default=datetime.now().strftime('%H:%M'), type=str)
    # app.logger.info(f"origin: {origin_object}")
    # app.logger.info(f"destination: {dest_object}")
    # app.logger.info(f"date: {date}")
    # app.logger.info(f"time: {time}")

    origin = f"{origin_object['geoloc']}"
    dest = f"{dest_object['geoloc']}"

    # compute shortest public transport trip
    public_transport_trips = get_trips_by_origin_and_destination(origin, dest, date, time)

    shortest_pt_trip = dict()
    if 'trips' in public_transport_trips:
        smallest = 0
        shortest_time = 100000000
        for i, trip in enumerate(public_transport_trips['trips']):
            trip_duration = isodate.parse_duration(trip['duration']).seconds
            if trip_duration < shortest_time:
                shortest_time = trip_duration
                smallest = i
        shortest_pt_trip = public_transport_trips['trips'][smallest]

    # app.logger.info("The smallest duration by public transportation is "
    #                 + f"{isodate.parse_duration(shortest_pt_trip['duration'])}")

    # compute duration of car trip
    (_, car_duration, car_distance) = get_time_by_car_only(
        ast.literal_eval(origin), ast.literal_eval(dest))
    # app.logger.info("The smallest duration by car is "
    #         +f"{timedelta(seconds=car_duration)}")

    # compute mix duration
    p_plus_rs = get_n_closest_pplusr(ast.literal_eval(origin))

    final_trips = []

    trip_mixed = {}
    if len(p_plus_rs) > 0:
        # print("For each PR, computing CFF paths")
        for parking in p_plus_rs:
            parking_data = parking[0]
            p_plus_r_geopos = parking_data['geometry']['coordinates']

            _, car_duration, car_distance = get_time_by_car_only(
                ast.literal_eval(origin), p_plus_r_geopos)

            timestamp = datetime.combine(
                datetime.strptime(date, '%Y-%m-%d'), datetime.strptime(time, '%H:%M').time())

            timestamp += timedelta(seconds=car_duration)

            trips = get_trips_by_origin_and_destination(
                f"{p_plus_r_geopos}",
                dest, date=timestamp.strftime('%Y-%m-%d'), time=timestamp.strftime('%H:%M'))

            for trip in trips['trips']:

                cff_duration = isodate.parse_duration(trip['duration']).seconds

                trip_list = [origin, dest, parking_data,
                             trip, round(car_duration+cff_duration), (car_distance / 1000) * 97]
                final_trips.append(trip_list)

        # print("Get the best path : home -> PR -> dest (via CFF)")
        fastest = final_trips[0]
        first_to_arrive = final_trips[0]
        earlier = None

        for trip in final_trips[1:]:
            end_time = None
            if trip[3]['legs'][-1]['type'] == "PTRideLeg":
                end_time = trip[3]['legs'][-1]['serviceJourney']['stopPoints'][-1]['arrival']['timeAimed']
            else:
                end_time = trip[3]['legs'][-1]['end']['timeAimed']

            # print(trip[3]['legs'][0]['start']['timeAimed'], " -> ",
            #       end_time, " : ", trip[-1])
            if trip[-1] < fastest[-1]:
                # print("got a fastest")
                fastest = trip

            if earlier is None or end_time < earlier:
                # print("go an earlier arriving")
                first_to_arrive = trip
                earlier = end_time

        trip_mixed = {
        'originName': origin_object['name'],
        'destinationName': dest_object['name'],
        'departure_time':  datetime.combine(
            datetime.strptime(date, '%Y-%m-%d'), datetime.strptime(time, '%H:%M').time()),
        'arrival_time': earlier,
        'legs': return_legs(first_to_arrive[3]['legs']), 
        'co2Emission': first_to_arrive[3]['ecoBalance']['co2Train'] + first_to_arrive[5]
        }
    time_pt_arrival = None

    if shortest_pt_trip['legs'][-1]['type'] == "PTRideLeg":
        time_pt_arrival = shortest_pt_trip['legs'][-1]['serviceJourney']['stopPoints'][-1]['arrival']['timeAimed']
    else:
        time_pt_arrival = shortest_pt_trip['legs'][-1]['end']['timeAimed']

    trip_full_cff = {
        'originName': origin_object['name'],
        'destinationName': dest_object['name'],
        'departure_time':  datetime.combine(
            datetime.strptime(date, '%Y-%m-%d'), datetime.strptime(time, '%H:%M').time()),
        'arrival_time': time_pt_arrival,
        'legs': return_legs(shortest_pt_trip['legs']),
        'co2Emission': shortest_pt_trip['ecoBalance']['co2Train']
    }

    trip_full_car = {
        'originName': origin_object['name'],
        'destinationName': dest_object['name'],
        'departure_time':  datetime.combine(
            datetime.strptime(date, '%Y-%m-%d'), datetime.strptime(time, '%H:%M').time()),
        'arrival_time': car_duration,
        'legs': [],
        # 97g of co2 per kilometer (average carbon emission)
        'co2Emission': car_distance/1000 * 97
    }

    return [trip_full_cff, trip_full_car, trip_mixed]


def get_time_by_car_only(origin: [float], dest: [float]) -> (datetime, float, float):
    '''
        Call Open Route Service to get the route between origin and dest
    '''

    headers = {
        'Authorization': ORS_API_KEY,
        'accept': 'application/json; charset=utf-8',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    body = {'coordinates': [origin, dest]}

    response = requests.post(
        ORS_API_URL + "/v2/directions/driving-car", headers=headers, json=body, timeout=2)

    routes = response.json()['routes']
    if len(routes) < 1:
        # print("No routes found between provided geopoints")
        return None, None, None

    itinerary = routes[0]
    distance = round(itinerary['summary']['distance'], 2)
    duration = round(itinerary['summary']['duration'] * TRAFFIC_FACTOR, 2)
    eta = datetime.now() + timedelta(seconds=duration)

    return eta, duration, distance


def get_trips_by_origin_and_destination(
    origin,
    destination,
    date,
    time
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


def get_n_closest_pplusr(geoloc, max_dist=MAX_PR_DISTANCE, num_closest=NUM_CLOSEST_PRS):
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
                target_lat, target_lon, entry['geometry']['coordinates'][1],
                entry['geometry']['coordinates'][0])

            if distance <= float(max_dist):
                distances.append([entry, distance])

        # Sort the locations by distance
        sorted_locations = sorted(distances, key=lambda x: x[1])

        # Get the closest locations (first num_closest elements)
        closest_locations = sorted_locations[:num_closest]

    return closest_locations


def return_legs(shortest_trip):

    parsed_legs = []
    for leg in shortest_trip:
        if leg['type'] == "PTRideLeg":
            parsed_leg = {
                'originName': f"{leg['serviceJourney']['stopPoints'][0]['place']['name']}, {leg['serviceJourney']['stopPoints'][0]['place']['canton']}",
                'destinationName': f"{leg['serviceJourney']['stopPoints'][-1]['place']['name']}, {leg['serviceJourney']['stopPoints'][-1]['place']['canton']}",
                'departure_time': leg['serviceJourney']['stopPoints'][0]['departure']['timeAimed'],
                'duration': isodate.parse_duration(leg['duration']).seconds,
                'arrival_time': leg['serviceJourney']['stopPoints'][-1]['arrival']['timeAimed'],
            }
            parsed_legs.append(parsed_leg)
            continue
        parsed_leg = {
            'originName': f"{leg['start']['place']['name']}, {leg['start']['place']['canton']}",
            'destinationName': f"{leg['end']['place']['name']}, {leg['end']['place']['canton']}",
            'departure_time': leg['start']['timeAimed'],
            'duration': isodate.parse_duration(leg['duration']).seconds,
            'arrival_time': leg['end']['timeAimed'],
        }
        parsed_legs.append(parsed_leg)
    return parsed_legs
