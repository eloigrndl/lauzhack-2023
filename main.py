'''
    Main pipepline for the GPS
'''
import json
import isodate
from cff_api_calls import get_closest_PRs_with_new_dataset, get_time_only_car, get_trip_by_origin_and_destination
from utils import format_json


if __name__ == "__main__":
    print("Let's go...")

    origin = [6.033765, 46.216143]
    destination = [6.629321, 46.517300]

    edges = []

    print("Getting closest PRs...")
    PRs = get_closest_PRs_with_new_dataset(origin)

    final_trips = []

    print("For each PR, computing CFF paths")
    for parking in PRs:
        parking_data = parking[0]
        parking_distance = parking[1]
        PR_geopos = parking_data['geometry']['coordinates']

        car_eta, car_duration, car_distance = get_time_only_car(
            origin, PR_geopos)

        trips = get_trip_by_origin_and_destination(
            f"{PR_geopos}", f"{destination}", date=car_eta.strftime('%Y-%m-%d'), time=car_eta.strftime('%H:%M'))

        json_to_dump = trips['trips'][0]
        print(format_json(json_to_dump))
        break
        for trip in trips['trips']:

            cff_duration = isodate.parse_duration(trip['duration']).seconds

            trip_list = [origin, destination, parking_data,
                         trip, round(car_duration+cff_duration)]
            final_trips.append(trip_list)

    print("Get the best path : home -> PR -> dest (via CFF)")
    best = final_trips[0]
    for trip in final_trips[1:]:
        if trip[-1] < best[-1]:
            best = trip

    with open("final_trip.json", 'w', encoding='utf-8') as file:
        json.dump(best, file)
