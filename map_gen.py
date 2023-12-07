import folium
import json

# Sample list of coordinates (latitude, longitude)
coordinates = [
    (40.7128, -74.0060),  # New York City
    (34.0522, -118.2437),  # Los Angeles
    (51.5074, -0.1278),   # London
    (48.8566, 2.3522)     # Paris
]

f = open("data/parking-facilities.json", 'r', encoding='utf-8')

data = json.load(f)

parkings = data['features']

print(parkings[0]['geometry']['coordinates'])
print(parkings[0]['geometry']['coordinates'][::-1])

coordinates = [x['geometry']['coordinates'][::-1] for x in parkings]


# Create a map centered at a specific location (in this case, New York City)
mymap = folium.Map(location=coordinates[0], zoom_start=8)

# Add markers for each coordinate in the list
for coord in coordinates:
    folium.Marker(location=coord, popup=str(coord)).add_to(mymap)

# Save the map as an HTML file
mymap.save("map_with_pins.html")
