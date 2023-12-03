# Lauzhack 2023 : SBB Challenge

### Install requirements

```
python3 -m venv env
source env/bin/activate

pip3 install -r requirements.txt
```

To run without any issue, set the following env. variables in the root folder :
- JOURNEY_API_URL = "https://journey-service-int.api.sbb.ch"
- CLIENT_SECRET = "..."
- CLIENT_ID = "..."
- SCOPE = "..."
- TOKEN_URL = "..."
- OPEN_ROUTE_API_KEY = "..."
- OPEN_ROUTE_API_URL = "https://api.openrouteservice.org"

and the following env. variables in the `cff-client` folder:
- REACT_APP_PLACE_API_URL = "http://127.0.0.1:5000/v1/places/by-name"
- REACT_APP_TRIPS_API_URL = "http://127.0.0.1:5000/v1/trips/by-origin-destination"

### Dataset

Dataset from https://opentransportdata.swiss/en/dataset/parking-facilities. Note it is not exactly the one provided initially in the challenge.

### Launch

The project works with a Flask server and a React/TailwindCSS client implementation. One has to launch both in order to have a working service.

First, launch the server : just type `flask run` at the root of the project : this will start the `app.py` file.

To client the client, go in the client directory (`cd cff-client`) and run the following commands :

- `npm i`
- `npm start`

Connect to the client on your browser via `https://localhost:3000`. This will pop a UI with which you will be able to interact.

&rarr; Be sure to have all the required libraries in order for the code to run smoothly as well `node.js` installed on your computer.

### How everything works

The goal of the project was to offer new ways to travel by combining Park and rails and train. Park and rails (P+R) are parkings close to train station in which customers can park while combining the price with the price of a train ticket, reducing the overall cost and the co2 emission.

We first gather informations about the Park and rails via the [opentransportdata.swiss](https://opentransportdata.swiss/en/dataset/parking-facilities) : this dataset includes about 560 Park and rails accross Switzerland. It is being updated daily so the dataset might get more points in the future.

When a user wants to compute a new itinerary, it will compute 3 types of routes :

- routes only using car.
- routes only using public transports.
- routes where the user will first ride to a nearby Park and rails and then take public transportation.

Car routes are computed using OpenRouteService API.
Public transport routes are computed using the SBB provided APIs.

To compute the combined routes, we do as follows:

- filter the nearest Park+Rails given the position/address of the user.
- compute the time and distance to all those Park and rails by car.
- compute trips from the Park and rails to destination via the SBB APIs.

This gives us several paths to different Park and rails and from each of them different train routes to the destination. Then we can compute the overall duration of the combined route.

In the end, the user gets 3 paths to choose from :

- only using their car.
- only using train.
- going to the nearest P+R and taking a train from there.

By Eloi Garandel, Jérémie Frei, Gaétan Hessler, Sébastien Hauri
