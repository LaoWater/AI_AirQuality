import requests
import base64
import json

# Step 1: Function to encode image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Step 2: Send Image to LLaVA via Ollama API
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

# Step 3: Example usage of the function
image_path = "traffic_map.png"  # Replace with the path to your image
result = send_image_to_ollama(image_path)
print(result)
