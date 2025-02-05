import requests

# API Token
API_TOKEN = "630496d0e81893c90d499ecebb81ab66b12b91ed"
CITY = "Cluj"

# API URL
url = f"https://api.waqi.info/feed/{CITY}/?token={API_TOKEN}"

# Make Request
response = requests.get(url)

# Parse Response
if response.status_code == 200:
    data = response.json()
    if data.get("status") == "ok":
        print("Air Quality Data for Cluj:")
        print(data)
    else:
        print(f"Error: {data.get('data', 'Unknown error')}")
else:
    print(f"Request failed with status code {response.status_code}")



# API URL to get stations
stations_url = f"https://api.waqi.info/search/?token={API_TOKEN}&keyword={CITY}"

# Make Request
stations_response = requests.get(stations_url)

# Parse Response
if stations_response.status_code == 200:
    stations_data = stations_response.json()
    if stations_data.get("status") == "ok":
        print("Monitoring Stations in Cluj:")
        print(stations_data)
    else:
        print(f"Error: {stations_data.get('data', 'Unknown error')}")
else:
    print(f"Request failed with status code {stations_response.status_code}")
