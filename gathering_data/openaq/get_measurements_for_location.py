import requests
import pandas as pd
import json
from math import radians, sin, cos, sqrt, atan2

# API URLs and key
BASE_URL = "https://api.openaq.org/v3"
LOCATIONS_API_URL = f"{BASE_URL}/locations"
MEASUREMENTS_API_URL = f"{BASE_URL}/sensors"  # We'll append /{sensor_id}/measurements

API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"
headers = {"X-API-Key": API_KEY}


def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on Earth (in meters) using the Haversine formula."""
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def get_locations_near(lat, lon, radius=12000, limit=10):
    """
    Fetch air quality locations near a given coordinate using a point and radius query.
    Computes the distance from the starting coordinates for each location.
    """
    url = f"{LOCATIONS_API_URL}?coordinates={lat},{lon}&radius={radius}&limit={limit}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["results"]
        df = pd.DataFrame(data)

        # Compute distance for each location
        df["distance"] = df["coordinates"].apply(
            lambda coords: haversine(lat, lon, coords.get("latitude"), coords.get("longitude"))
        )
        # Sort by computed distance
        df = df.sort_values("distance")
        return df.to_dict(orient="records")
    else:
        print("Error fetching locations near coordinates:", response.status_code, response.text)
        return None


def get_latest_measurement_for_sensor(sensor_id):
    """
    Fetch the latest measurement for a given sensor by its id.
    We use order_by datetime (descending) and limit=1.
    """
    url = f"{MEASUREMENTS_API_URL}/{sensor_id}/measurements"
    params = {
        "limit": 1,
        "order_by": "datetime",
        "sort": "desc"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        return results[0] if results else None
    else:
        print(f"Error fetching measurements for sensor {sensor_id}:", response.status_code, response.text)
        return None


def get_latest_measurements_for_location(location):
    """
    For a given location (dict), iterate over its sensors and fetch the latest measurement for each sensor.
    Returns a dict keyed by sensor id with the measurement data.
    """
    measurements = {}
    sensors = location.get("sensors", [])
    for sensor in sensors:
        sensor_id = sensor.get("id")
        if sensor_id:
            meas = get_latest_measurement_for_sensor(sensor_id)
            measurements[sensor_id] = meas
    return measurements


def main():
    # Coordinates for Bucharest, for example.
    lat, lon = 44.4268, 26.1025
    locations = get_locations_near(lat, lon, radius=12000, limit=10)

    if not locations:
        print("No locations found.")
        return

    # For each location, get the latest measurements for all its sensors
    results = []
    for loc in locations:
        loc_entry = {
            "location_id": loc.get("id"),
            "name": loc.get("name"),
            "locality": loc.get("locality"),
            "distance": loc.get("distance"),
            "coordinates": loc.get("coordinates"),
            "sensors": []
        }
        sensors = loc.get("sensors", [])
        for sensor in sensors:
            sensor_id = sensor.get("id")
            sensor_info = sensor.copy()  # copy the sensor metadata
            measurement = get_latest_measurement_for_sensor(sensor_id)
            sensor_info["latest_measurement"] = measurement
            loc_entry["sensors"].append(sensor_info)
        results.append(loc_entry)

    # Save aggregated results to a JSON file with proper encoding for special characters.
    json_filename = "latest_sensor_data.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved latest sensor data to '{json_filename}'.")


if __name__ == "__main__":
    main()
