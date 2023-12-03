'''
    Utils package with helper function
'''

import os
import json
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime, timedelta
import requests

# Access variables
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
SCOPE = os.getenv("SCOPE")
TOKEN_URL = os.getenv("TOKEN_URL")

# Token file
token_filename = absolute_path = os.path.abspath('sbb_token.json')


def format_json(json_to_print):
    '''
        print pretty json
    '''
    return json.dumps(json_to_print, indent=1)


def haversine_formula(lat1, lon1, lat2, lon2):
    '''
        Compute haversine forumla for given coordinates
    '''
    # Radius of the Earth in kilometers
    r = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula to calculate distance
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = r * c

    return distance


def get_token():
    '''
        Check if token is on computer and if it is valid
        If not, calls fetch_token()
    '''

    # Try to get the token locally
    try:
        # Open the token file
        with open(token_filename, 'r', encoding='utf-8') as file:
            token = json.load(file)
            try:
                # get expiration time
                expiration_time = datetime.strptime(
                    token['expiration_time'], "%Y-%m-%d %H:%M:%S")

                time_diff = (expiration_time - datetime.now()
                             ).total_seconds()/60

                if time_diff < 3:
                    # Token expires in 3 minutes -> fetch a new one
                    print("Token almost expired -> fetching")
                    return fetch_token()

                # Token still good -> return the current one
                return token['access_token']
            except KeyError:
                print("Problem with token file -> fetching new token")
                return fetch_token()

    except FileNotFoundError:
        print("No local token found -> query for token")
        return fetch_token()


def fetch_token():
    '''
        Fetch and store token from URL
    '''

    params = {
        'grant_type': 'client_credentials',
        'scope': SCOPE,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    token_response = requests.post(TOKEN_URL,
                                   data=params, timeout=0.5)

    # If no problem, should fetch the token online
    assert token_response.status_code == 200

    token_json = token_response.json()

    try:

        # Computes expiration time
        expiration_time = datetime.now(
        ) + timedelta(seconds=token_json['expires_in'])
        token_json['expiration_time'] = expiration_time.strftime(
            "%Y-%m-%d %H:%M:%S")

        # Write token in file
        with open(token_filename, 'w', encoding='utf-8') as file:
            json.dump(token_json, file)

        # Return newly fetched token
        return token_json['access_token']

    except KeyError:
        print("Error fetching token online")
        return None


def format_date(datetime_to_format):
    '''
        Convert datetime to string
    '''
    return datetime_to_format.strftime("%Y-%m-%d %H:%M:%S")
