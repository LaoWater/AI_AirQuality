import requests
import pandas as pd

# OpenAQ API URL for locations
LOCATIONS_API_URL = "https://api.openaq.org/v3/locations"

# Your OpenAQ API Key
API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"

# Headers required for authentication
headers = {"X-API-Key": API_KEY}

def get_locations_in_bbox(bbox, limit=10):
    """Fetch air quality locations inside a given bounding box."""
    url = f"{LOCATIONS_API_URL}?bbox={bbox}&limit={limit}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("\nFull API Response JSON:", data)

        if "results" in data and data["results"]:
            df = pd.DataFrame(data["results"])
            print("\nDataFrame Column Names:", df.columns)

            available_columns = [col for col in ["id", "name", "locality", "timezone", "country"] if col in df.columns]
            if available_columns:
                print(df[available_columns])
            else:
                print("No expected columns found in API response.")

            return df
        else:
            print("No air quality monitoring locations found in this bounding box.")
            return None
    else:
        print("Error fetching locations in bounding box:", response.status_code, response.text)
        return None

if __name__ == "__main__":
    bbox_london = "-0.2,51.4,-0.1,51.6"
    get_locations_in_bbox(bbox_london)
