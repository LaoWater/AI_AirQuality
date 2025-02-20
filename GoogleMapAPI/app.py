import requests
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CITY = "Cluj-Napoca, str. Cetatii, Floresti"

# Step 1: Get Coordinates of the City
geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={CITY}&key={GOOGLE_API_KEY}"
geo_response = requests.get(geocode_url).json()

if geo_response["status"] == "OK":
    location = geo_response["results"][0]["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]
    print(f"📍 Coordinates of {CITY}: {lat}, {lng}\n")

    # Step 2: Get Traffic Data in a 200m Area
    origin = f"{lat},{lng}"
    destination = f"{lat+0.0018},{lng}"  # ~200m north
    traffic_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&departure_time=now&key={GOOGLE_API_KEY}"

    traffic_response = requests.get(traffic_url).json()

    if traffic_response["status"] == "OK":
        # Extract travel durations
        route = traffic_response["routes"][0]["legs"][0]
        duration = route["duration"]["value"]  # Normal duration (seconds)
        duration_traffic = route.get("duration_in_traffic", {}).get("value", duration)  # Traffic duration

        # Calculate traffic congestion level
        delay = duration_traffic - duration
        congestion_level = "🚗 Light Traffic"

        if delay > duration * 0.5:  # If delay is 50% or more
            congestion_level = "🚦 Heavy Traffic"
        elif delay > duration * 0.2:  # If delay is 20% or more
            congestion_level = "⛔ Moderate Traffic"

        # Print results
        print(f"🚦 Normal Duration: {duration//60} min {duration%60} sec")
        print(f"🛑 Duration in Traffic: {duration_traffic//60} min {duration_traffic%60} sec")
        print(f"📊 Estimated Traffic Congestion: {congestion_level}")

    else:
        print("❌ Error fetching traffic data:", traffic_response["status"])

else:
    print("❌ Error fetching location:", geo_response["status"])
