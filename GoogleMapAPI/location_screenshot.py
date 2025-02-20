import requests
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load API keys from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CITY = "Floresti, Cetatii, 3A"

# Step 1: Get Coordinates of the City
geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={CITY}&key={GOOGLE_API_KEY}"
geo_response = requests.get(geocode_url).json()

if geo_response["status"] == "OK":
    location = geo_response["results"][0]["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]
    print(f"📍 Coordinates of {CITY}: {lat}, {lng}")

    # Step 2: Get Static Map Screenshot (50m radius)
    zoom_level = 18  # Higher zoom = closer view (~50m)
    map_size = "600x600"  # Image resolution
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom_level}&size={map_size}&maptype=roadmap&markers=color:red%7C{lat},{lng}&key={GOOGLE_API_KEY}"

    # Download and save the map image
    response = requests.get(map_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image_path = "traffic_map.png"
        image.save(image_path)
        print(f"📸 Screenshot saved: {image_path}")
        image.show()  # Open the image
    else:
        print("❌ Error fetching map image:", response.status_code)

else:
    print("❌ Error fetching location:", geo_response["status"])
