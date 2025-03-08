import os
from dotenv import load_dotenv
import requests
import math
import json

# Load environment variables from .env file
load_dotenv()

# API Token from .env
API_TOKEN = os.getenv("aqi_cn_token")
if not API_TOKEN:
    raise ValueError("API token not found. Ensure 'aqi_cn_token' is set in the .env file.")


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points (in kilometers)."""
    R = 6371.0  # Earth radius in km
    from math import radians, sin, cos, sqrt, atan2
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def get_nearest_aqi_points(latitude, longitude, token, num_points=3, initial_radius_km=10, step_km=10):
    """
    Expands the search in a circular area until at least `num_points` are found.
    The search starts with an initial radius (in km) and expands by `step_km` increments.
    """
    radius_km = initial_radius_km
    while True:
        # Convert the current radius to a degree offset (approximation: 1° ≈ 111 km)
        delta = radius_km / 111
        lat_min = latitude - delta
        lat_max = latitude + delta
        lng_min = longitude - delta
        lng_max = longitude + delta

        # Use the map/bounds endpoint from documentation
        map_url = (
            f"https://api.waqi.info/v2/map/bounds?"
            f"latlng={lat_min},{lng_min},{lat_max},{lng_max}&networks=all&token={token}"
        )
        response = requests.get(map_url)
        data = response.json()
        print("Response: ", data)  # Debug: print raw API response

        if data.get("status") != "ok":
            raise Exception("Error fetching data from API: " + str(data.get("data", "Unknown error")))

        points = data.get("data", [])
        valid_points = []
        # Filter points to include only those within the circular radius
        for point in points:
            point_lat = point.get("lat")
            point_lon = point.get("lon")
            dist = haversine_distance(latitude, longitude, point_lat, point_lon)
            point["distance"] = dist
            if dist <= radius_km:
                valid_points.append(point)

        # If we have enough points, return the nearest ones (sorted by distance)
        if len(valid_points) >= num_points:
            sorted_points = sorted(valid_points, key=lambda x: x["distance"])
            return sorted_points[:num_points]

        # Otherwise, expand the radius and try again
        radius_km += step_km


def extract_relevant_data(points):
    """
    Extracts station name and the last measures for O₃, PM₁₀, PM₂.₅, NO₂, and CO₂.
    """
    extracted_data = []
    for point in points:
        iaqi = point.get("iaqi", {})
        station_name = point.get("station", {}).get("name") or point.get("city", {}).get("name")
        data_entry = {
            "station": station_name,
            "O3": iaqi.get("o3", {}).get("v") if "o3" in iaqi else None,
            "PM10": iaqi.get("pm10", {}).get("v") if "pm10" in iaqi else None,
            "PM2.5": iaqi.get("pm25", {}).get("v") if "pm25" in iaqi else None,
            "NO2": iaqi.get("no2", {}).get("v") if "no2" in iaqi else None,
            "CO2": iaqi.get("co2", {}).get("v") if "co2" in iaqi else None
        }
        extracted_data.append(data_entry)
    return extracted_data


def get_station_feed(station_id, token):
    """
    Retrieves the real-time feed data for a given station using its ID.
    The feed endpoint expects an id prefixed with '@'.
    """
    feed_url = f"https://api.waqi.info/feed/@{station_id}/?token={token}"
    response = requests.get(feed_url)
    feed_data = response.json()
    print(f"Feed response for station id '@{station_id}':", feed_data)  # Debug: print feed response
    if feed_data.get("status") != "ok":
        print(f"Error retrieving feed data for station id '@{station_id}': {feed_data.get('data')}")
        return None
    return feed_data.get("data")


if __name__ == "__main__":
    # User's coordinates (home location)
    latitude = 46.7445701195037
    longitude = 23.49587497922032

    try:
        # Get the 3 nearest AQI stations (from the map/bounds API)
        nearest_points = get_nearest_aqi_points(latitude, longitude, API_TOKEN)

        # Save basic station data to JSON (from the map/bounds API)
        basic_data = extract_relevant_data(nearest_points)
        with open("aqi_data.json", "w") as f:
            json.dump(basic_data, f, indent=4)
        print("Basic station data saved to aqi_data.json")

        # For each of the nearest stations, get detailed feed data using station id
        detailed_feeds = []
        for point in nearest_points:
            station_id = point.get("uid")
            station_name = point.get("station", {}).get("name") or point.get("city", {}).get("name")
            feed = get_station_feed(station_id, API_TOKEN)
            if feed:
                detailed_feeds.append({
                    "station": station_name,
                    "id": station_id,
                    "data": feed
                })

        with open("aqi_feed_data.json", "w") as f:
            json.dump(detailed_feeds, f, indent=4)
        print("Detailed station feed data saved to aqi_feed_data.json")
    except Exception as e:
        print("Error:", e)
