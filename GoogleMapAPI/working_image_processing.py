import requests
import os
import base64
import json
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

        # Step 3: Function to encode image to Base64
        def encode_image_to_base64(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Step 4: Send Image to LLaVA via Ollama API
        def send_image_to_ollama(image_path):
            base64_image = encode_image_to_base64(image_path)

            payload = {
                "model": "llava",
                "prompt": "What do you see in this image?",
                "images": [base64_image]
            }

            headers = {"Content-Type": "application/json"}
    
            try:
                response = requests.post("http://localhost:11434/api/generate", json=payload, headers=headers)
        
                # Print the raw response for debugging
                print("Raw LLaVA Response:", response.text)
        
                # Split the response text into lines and parse each line as JSON
                try:
                    lines = response.text.strip().split("\n")
                    responses = [json.loads(line) for line in lines]

                    # Concatenate all parts of the response into a single string
                    combined_text = " ".join(entry["response"] for entry in responses)

                    return f"🚀 LLaVA Model Response: {combined_text}"
        
                except json.JSONDecodeError:
                    return "❌ Error decoding JSON response from LLaVA"
    
            except requests.exceptions.RequestException as e:
                return f"❌ Request error while sending to LLaVA: {e}"

        # Step 5: Example usage of the function
        result = send_image_to_ollama(image_path)
        print(result)

    else:
        print("❌ Error fetching map image:", response.status_code)

else:
    print("❌ Error fetching location:", geo_response["status"])
