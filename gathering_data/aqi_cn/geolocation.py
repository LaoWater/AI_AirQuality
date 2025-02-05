import requests

# API Token
API_TOKEN = "630496d0e81893c90d499ecebb81ab66b12b91ed"

# User's coordinates (home location)
latitude = 46.765425
longitude = 23.550258

# API URLs
geo_url = f"https://api.waqi.info/feed/geo:{latitude};{longitude}/?token={API_TOKEN}"
# Expanding the boundary (increase from 0.1 to 0.5)
lat_min = latitude - 2
lat_max = latitude + 2
lng_min = longitude - 2
lng_max = longitude + 2

# Updated API URL for wider area
map_url = f"https://api.waqi.info/map/bounds?token={API_TOKEN}&latlng={lat_min},{lng_min},{lat_max},{lng_max}"


# Making API requests
geo_response = requests.get(geo_url)
map_response = requests.get(map_url)

# Parsing Responses
geo_data = geo_response.json() if geo_response.status_code == 200 else None
map_data = map_response.json() if map_response.status_code == 200 else None

# Display Results
print("\n===== Geolocated Air Quality Data =====")
print(geo_data)

print("\n===== Air Quality Stations in Area =====")
print(map_data)
