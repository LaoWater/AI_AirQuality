#!/usr/bin/env python
import requests
import pandas as pd

# OpenAQ API URL for locations
LOCATIONS_API_URL = "https://api.openaq.org/v3/locations"

# Your OpenAQ API Key
API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"

# Headers required for authentication
headers = {"X-API-Key": API_KEY}


def get_locations_in_bbox(bbox, limit=10):
    """
    Fetch air quality monitoring locations within a given bounding box.

    The bounding box should be provided as a comma-delimited string of 4 WGS84 coordinates:
    "min_longitude,min_latitude,max_longitude,max_latitude".

    Parameters:
        bbox (str): Bounding box coordinates.
        limit (int): Maximum number of results to return.

    Returns:
        pd.DataFrame: A DataFrame containing the location data.
    """
    url = f"{LOCATIONS_API_URL}?bbox={bbox}&limit={limit}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["results"]
        df = pd.DataFrame(data)
        print(f"\nLocations inside bounding box {bbox}:")

        # Print selected columns. Adjust the column list as needed.
        try:
            print(df[["id", "name", "city", "country"]])
        except KeyError:
            # In case some of the expected columns are not present, print the full DataFrame.
            print("Some expected columns are missing. Here's the full DataFrame:")
            print(df)
        return df
    else:
        print("Error fetching locations in bounding box:", response.status_code, response.text)
        return None


if __name__ == "__main__":
    # Example bounding box: around Accra, Ghana.
    # Format: "min_longitude,min_latitude,max_longitude,max_latitude"
    bbox = "5.488869,-0.396881,5.732144,-0.021973"
    get_locations_in_bbox(bbox, limit=10)
