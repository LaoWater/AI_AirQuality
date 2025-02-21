import requests
import os
import json
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Token from .env
API_TOKEN = os.getenv("aqi_cn_token")
if not API_TOKEN:
    raise ValueError("API token not found. Ensure 'aqi_cn_token' is set in the .env file.")

# User's coordinates (home location)
latitude = 46.765425
longitude = 23.550258

# API URLs
geo_url = f"https://api.waqi.info/feed/geo:{latitude};{longitude}/?token={API_TOKEN}"

# Expanding the boundary (increase from 0.1 to 0.5 for a wider area)
lat_min = latitude - 0.3
lat_max = latitude + 0.3
lng_min = longitude - 0.3
lng_max = longitude + 0.3
map_url = f"https://api.waqi.info/map/bounds?token={API_TOKEN}&latlng={lat_min},{lng_min},{lat_max},{lng_max}"

# Making API requests
geo_response = requests.get(geo_url)
map_response = requests.get(map_url)

# Parsing Responses (only if status is 200)
geo_data = geo_response.json() if geo_response.status_code == 200 else None
map_data = map_response.json() if map_response.status_code == 200 else None

import json

# Pretty print the API responses to the console
print("\n===== Geolocated Air Quality Data =====")
print(json.dumps(geo_data, indent=4))

print("\n===== Air Quality Stations in Area =====")
print(json.dumps(map_data, indent=4))

# Save the Geolocated Air Quality Data to a JSON file
with open("geo_data.json", "w") as geo_file:
    json.dump(geo_data, geo_file, indent=4)
print("Geolocated Air Quality Data saved to geo_data.json")

# Save the Air Quality Stations data to a JSON file
with open("map_data.json", "w") as map_file:
    json.dump(map_data, map_file, indent=4)
print("Air Quality Stations data saved to map_data.json")

# ----------------------------
# Plotting Forecast Data for PM10
# ----------------------------

# Extract PM10 forecast data from the API response
forecast_pm10 = geo_data.get("data", {}).get("forecast", {}).get("daily", {}).get("pm10", [])
if forecast_pm10:
    # Extracting days and corresponding PM10 values
    days = [item["day"] for item in forecast_pm10]
    pm10_avg = [item["avg"] for item in forecast_pm10]
    pm10_max = [item["max"] for item in forecast_pm10]
    pm10_min = [item["min"] for item in forecast_pm10]

    # Define a normal PM10 threshold (e.g., WHO 24-hour guideline ~50 µg/m³)
    normal_pm10 = 50

    plt.figure(figsize=(10, 6))
    plt.plot(days, pm10_avg, label="Average PM10", marker="o", color="blue")
    plt.fill_between(days, pm10_min, pm10_max, color="skyblue", alpha=0.3, label="Min/Max PM10")
    plt.axhline(y=normal_pm10, color="red", linestyle="--", label="Normal PM10 Level (50 µg/m³)")
    plt.xlabel("Day")
    plt.ylabel("PM10 Levels (µg/m³)")
    plt.title("PM10 Forecast for Cluj")
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    print("No PM10 forecast data available for plotting.")
