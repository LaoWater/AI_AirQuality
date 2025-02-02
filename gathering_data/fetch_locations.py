import requests
import pandas as pd
import json
from math import radians, sin, cos, sqrt, atan2

# OpenAQ API URL for locations
LOCATIONS_API_URL = "https://api.openaq.org/v3/locations"

# Your OpenAQ API Key
API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"

# Headers required for authentication
headers = {"X-API-Key": API_KEY}


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth (in meters)
    using the Haversine formula.
    """
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
    Computes the distance (in meters) from the starting coordinates for each location,
    sorts the locations by distance, and saves the result as formatted JSON to a file.
    """
    url = f"{LOCATIONS_API_URL}?coordinates={lat},{lon}&radius={radius}&limit={limit}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["results"]
        df = pd.DataFrame(data)

        # Compute the distance for each location using the Haversine formula.
        df["distance"] = df["coordinates"].apply(
            lambda coords: haversine(lat, lon, coords.get("latitude"), coords.get("longitude"))
        )

        # Sort the DataFrame by the computed distance.
        df = df.sort_values("distance")

        print(f"\nLocations near {lat}, {lon} (within {radius}m), sorted by distance:")
        # Print all columns, including the computed distance.
        print(df.to_string(index=False))

        # Convert the DataFrame to a list of dictionaries.
        results = df.to_dict(orient="records")

        # Save the formatted JSON to a file.
        json_filename = "get_near_locations.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


        print(f"Saved formatted JSON to '{json_filename}'")
        return df
    else:
        print("Error fetching locations near coordinates:", response.status_code, response.text)
        return None


if __name__ == "__main__":
    # Example: Save formatted JSON for locations near Bucharest (44.4268, 26.1025)
    get_locations_near(44.4268, 26.1025)
