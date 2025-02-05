# ID:74  RO  Romania
# ID:22 FR, ID:111 TH, ID:155 USA


import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Token from .env
API_KEY = os.getenv("openaq_token")


# OpenAQ API URL for countries
COUNTRIES_API_URL = "https://api.openaq.org/v3/countries"

# Headers required for authentication
headers = {"X-API-Key": API_KEY}


def get_country_list():
    """Fetch all available countries and their IDs from OpenAQ."""
    params = {"limit": 200, "page": 1}  # Fetch all countries
    response = requests.get(COUNTRIES_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        countries = response.json()["results"]
        df = pd.DataFrame(countries)

        # Ensure all rows are displayed
        pd.set_option("display.max_rows", None)  # Show all rows
        pd.set_option("display.max_columns", None)  # Show all columns if needed
        pd.set_option("display.width", 1000)  # Prevent line breaks

        print("\nAvailable Countries:")
        print(df[["id", "code", "name"]])

        # Check for the USA explicitly, as it was previously missing
        usa_data = df[df["code"].str.contains("US", case=False) | df["name"].str.contains("United States", case=False)]
        print("\nUSA Data:")
        print(usa_data)

        return df
    else:
        print("Error fetching country list:", response.status_code, response.text)
        return None



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



if __name__ == "__main__":
    get_country_list()