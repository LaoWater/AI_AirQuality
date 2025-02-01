import requests
import pandas as pd

# OpenAQ API URLs
CITIES_API_URL = "https://api.openaq.org/v3/cities"
AIR_QUALITY_API_URL = "https://api.openaq.org/v3/latest"

# Your API Key (Replace with your actual key)
API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"  # <-- Replace this with your actual API key

# Headers required for authentication
headers = {
    "X-API-Key": API_KEY
}

# Query parameters for location (Bucharest, Romania)
params = {
    "country": "RO",  # Romania
    "city": "Bucharest",
    "limit": 5,  # Get only 5 results for now
    "order_by": "date",
    "sort": "desc",
}


def get_locations_near(lat, lon, radius=12000, limit=10):
    """Fetch air quality locations near a given coordinate"""
    url = f"https://api.openaq.org/v3/locations?coordinates={lon},{lat}&radius={radius}&limit={limit}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["results"]
        df = pd.DataFrame(data)

        print("\nFull API Response Keys:", df.columns)  # Print all column names in response
        print(f"\nLocations near {lat}, {lon} (within {radius}m):")

        # Instead of selecting fixed columns, let's dynamically adjust based on the response
        possible_columns = ["id", "name", "city", "country", "location"]
        available_columns = [col for col in possible_columns if col in df.columns]

        if available_columns:
            print(df[available_columns])
        else:
            print("No expected columns found in API response.")

        return df
    else:
        print("Error fetching locations near coordinates:", response.status_code, response.text)
        return None


# Run function with example coordinates (Bucharest)
get_locations_near(44.4268, 26.1025)


def get_locations_in_bbox(bbox, limit=10):
    """Fetch air quality locations inside a given bounding box"""
    url = f"https://api.openaq.org/v3/locations?bbox={bbox}&limit={limit}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["results"]
        df = pd.DataFrame(data)
        print(f"\nLocations inside bounding box {bbox}:")
        print(df[["id", "name", "city", "country"]])
        return df
    else:
        print("Error fetching locations in bounding box:", response.status_code, response.text)
        return None


# Example Bounding Box (Bucharest Area)
bbox = "26.00,44.30,26.20,44.50"  # (minLon, minLat, maxLon, maxLat)
get_locations_in_bbox(bbox)


# 🚀 Run the function and display results
city = "Bucharest"  # Change this to any city name

available_cities = get_locations_near(44.4268, 26.1025)
print(available_cities)

