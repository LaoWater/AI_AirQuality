# ID:74  RO  Romania
# ID:22 FR, ID:111 TH, ID:155 USA


import requests
import pandas as pd

# OpenAQ API URL for countries
COUNTRIES_API_URL = "https://api.openaq.org/v3/countries"

# Your OpenAQ API Key
API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"

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


if __name__ == "__main__":
    get_country_list()