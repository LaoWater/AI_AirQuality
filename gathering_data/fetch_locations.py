import requests
import pandas as pd

# OpenAQ API URL for countries
COUNTRIES_API_URL = "https://api.openaq.org/v3/countries"

# Your OpenAQ API Key
API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"

# Headers required for authentication
headers = {"X-API-Key": API_KEY}


def get_country_info(country_id=74):
    """
    Fetch information about a country from the OpenAQ API using its unique country id.
    For Romania, the country id is assumed to be 74.
    """
    url = f"{COUNTRIES_API_URL}/{country_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("\nFull API Response JSON:")
        print(data)

        # The response payload contains a "results" key with a list of country objects.
        if "results" in data and data["results"]:
            df = pd.DataFrame(data["results"])
            print("\nDataFrame Column Names:", df.columns)

            # Display key fields: id, code, and name
            available_columns = [col for col in ["id", "code", "name"] if col in df.columns]
            if available_columns:
                print("\nCountry information:")
                print(df[available_columns])
            else:
                print("No expected columns found in API response.")
            return df
        else:
            print("No country information found.")
            return None
    else:
        print("Error fetching country info:", response.status_code, response.text)
        return None


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


if __name__ == "__main__":
    # For Romania, we use country_id=74
    get_country_info(country_id=74)
