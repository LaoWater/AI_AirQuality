import requests
import json
from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt

# -----------------------
# Configuration and API URLs
# -----------------------
BASE_URL = "https://api.openaq.org/v3"
LOCATIONS_API_URL = f"{BASE_URL}/locations"
MEASUREMENTS_API_URL = f"{BASE_URL}/sensors"  # We'll append /{sensor_id}/measurements
API_KEY = "129db180ca4d7cb90ff7ea6dfb5ee9156e43d344870f2c501297bf16b8906417"
headers = {"X-API-Key": API_KEY}


# -----------------------
# Helper Functions
# -----------------------
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance (in meters) between two points on Earth."""
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def get_near_locations(lat, lon, radius=12000, limit=10):
    """
    Retrieve nearby locations (up to limit) within the given radius (in meters),
    and compute the distance of each location from (lat, lon).
    """
    url = f"{LOCATIONS_API_URL}?coordinates={lat},{lon}&radius={radius}&limit={limit}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["results"]
        # Compute distance for each location.
        for loc in data:
            coords = loc.get("coordinates", {})
            loc["distance"] = haversine(lat, lon, coords.get("latitude"), coords.get("longitude"))
        # Sort locations by distance (nearest first).
        data.sort(key=lambda x: x["distance"])
        print("Near Locations Identified:")
        for loc in data:
            print(f"  - {loc.get('name')} (ID: {loc.get('id')}) at {loc.get('distance'):.0f} m")
        return data
    else:
        print("Error fetching near locations:", response.status_code, response.text)
        return []


def get_latest_measurement_for_sensor(sensor_id):
    """
    Retrieve the most recent measurement for the given sensor_id.
    We fetch a larger payload and then process the response to choose the latest measurement.
    """
    url = f"{MEASUREMENTS_API_URL}/{sensor_id}/measurements"
    params = {
        "limit": 100,  # request a larger payload
        "order_by": "datetimeFrom.utc",  # ordering by datetimeFrom.utc descending
        "sort": "desc"
    }
    response = requests.get(url, headers=headers, params=params)

    # Print the full API response for inspection
    print("Full Get_Latest_Measurements API response:")
    json_response = response.json()
    print(json_response)

    if response.status_code == 200:
        results = json_response.get("results", [])
        if not results:
            print(f"No measurement results for sensor {sensor_id}.")
            return None

        # Iterate over the results to find the measurement with the latest datetime
        latest_result = None
        latest_dt = None
        for meas in results:
            dt_str = None
            # Try to get the datetime from the "period" block
            period = meas.get("period", {})
            if isinstance(period.get("datetimeFrom"), dict):
                dt_str = period.get("datetimeFrom", {}).get("utc")
            elif isinstance(period.get("datetimeFrom"), str):
                dt_str = period.get("datetimeFrom")

            # Fallback: check if measurement has "datetimeFrom" at the top level
            if not dt_str:
                dt_str = meas.get("datetimeFrom")

            if dt_str:
                try:
                    # Replace 'Z' with '+00:00' so datetime.fromisoformat can parse it
                    dt_str_mod = dt_str.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(dt_str_mod)
                except Exception as e:
                    print(f"Error parsing datetime '{dt_str}' for sensor {sensor_id}: {e}")
                    continue
                if (latest_dt is None) or (dt > latest_dt):
                    latest_dt = dt
                    latest_result = meas

        if latest_result:
            print(f"Latest measurement for sensor {sensor_id}: {latest_result}")
            return latest_result
        else:
            print(f"No valid measurement datetime found for sensor {sensor_id}.")
            return None
    else:
        print(f"Error fetching latest measurement for sensor {sensor_id}: {response.status_code} {response.text}")
        return None


def process_location(location):
    """
    For a given location, iterate through its sensors and retrieve the latest measurement.
    Prints sensor information during processing.
    Returns a list of sensor measurement entries.
    Each entry contains:
      - sensor_id
      - parameter (the sensor's name)
      - measurement_value, units, and measurement_datetime (from the measurement record)
    """
    sensors = location.get("sensors", [])
    sensor_entries = []
    print(f"\nProcessing location: {location.get('name')} (ID: {location.get('id')})")
    print(f"Found {len(sensors)} sensor(s) at this location.")

    for sensor in sensors:
        sensor_id = sensor.get("id")
        sensor_name = sensor.get("name")
        if not sensor_id:
            continue
        print(f"  Fetching measurement for sensor: {sensor_id} - {sensor_name}")
        meas = get_latest_measurement_for_sensor(sensor_id)
        if meas:
            # Extract measurement timestamp (check both "period" and "datetime")
            measurement_datetime = None
            if meas.get("period") and meas["period"].get("datetimeTo"):
                dt_obj = meas["period"]["datetimeTo"]
                if isinstance(dt_obj, dict):
                    measurement_datetime = dt_obj.get("utc")
                elif isinstance(dt_obj, str):
                    measurement_datetime = dt_obj
            elif meas.get("datetime"):
                measurement_datetime = meas.get("datetime")

            sensor_entry = {
                "sensor_id": sensor_id,
                "parameter": sensor_name,
                "measurement_value": meas.get("value"),
                "units": meas.get("parameter", {}).get("units") if isinstance(meas.get("parameter"), dict) else None,
                "measurement_datetime": measurement_datetime
            }
            print(f"    Measurement: {sensor_entry}")
            sensor_entries.append(sensor_entry)
        else:
            print(f"    No measurement found for sensor {sensor_id}.")
    return sensor_entries


# -----------------------
# Plotting Function
# -----------------------
def plot_sensor_measurements(sensor_measurements):
    """
    Create a scatter plot of sensor measurement values.
    Each parameter is plotted on the x-axis (as discrete points) with a green shaded healthy range.
    """
    # Define example healthy ranges (modify as needed)
    healthy_ranges = {
        "co µg/m³": (0, 500),
        "no2 µg/m³": (0, 40),
        "o3 µg/m³": (0, 100),
        "pm10 µg/m³": (0, 50),
        "pm25 µg/m³": (0, 12),
        "so2 µg/m³": (0, 20)
    }

    # Extract unique parameters and assign x-axis positions.
    unique_params = []
    for meas in sensor_measurements:
        param = meas["parameter"]
        if param not in unique_params:
            unique_params.append(param)
    param_to_index = {param: i for i, param in enumerate(unique_params)}

    plt.figure(figsize=(10, 6))

    # Plot each measurement
    for meas in sensor_measurements:
        param = meas["parameter"]
        x = param_to_index[param]
        y = meas["measurement_value"]
        plt.scatter(x, y, s=100, color="blue", zorder=3)
        plt.text(x, y, f"{y:.1f}", fontsize=9, ha="center", va="bottom")

    # Set x-axis labels
    plt.xticks(range(len(unique_params)), unique_params, fontsize=10)
    plt.ylabel("Measurement Value", fontsize=12)
    plt.title("Sensor Measurements", fontsize=14)

    # Add healthy range shading for each parameter, if available
    for param, x in param_to_index.items():
        if param in healthy_ranges:
            low, high = healthy_ranges[param]
            plt.fill_between([x - 0.4, x + 0.4], low, high, color="green", alpha=0.2, zorder=1)
            plt.plot([x - 0.4, x + 0.4], [low, low], color="green", linestyle="--", zorder=2)
            plt.plot([x - 0.4, x + 0.4], [high, high], color="green", linestyle="--", zorder=2)

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("sensor_measurements_plot.png", dpi=300)
    plt.show()
    print("Plot saved as 'sensor_measurements_plot.png'.")


# -----------------------
# Main Workflow
# -----------------------
def main():
    # Popular coordinates for testing
    popular_coordinates = [
        {"name": "Home - Cluj", "lat": 46.74456, "lon": 23.49592},
        {"name": "Bucharest", "lat": 44.4268, "lon": 26.1025},
        {"name": "London", "lat": 51.5074, "lon": -0.1278},
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "Tokyo", "lat": 35.6895, "lon": 139.6917}
    ]

    # Change index to test different locations:
    selected = popular_coordinates[0]
    lat, lon = selected["lat"], selected["lon"]
    print(f"Testing with coordinate: {selected['name']} ({lat}, {lon})")

    # Retrieve up to 10 nearby locations
    near_locations = get_near_locations(lat, lon, radius=12000, limit=10)
    required_sensor_count = 6  # Adjust this threshold as needed

    candidate_locations = []
    for loc in near_locations:
        if loc.get("name") == "CJ-3":  # Filter for the specific location
            sensor_data = process_location(loc)
            print(f"Total sensors with measurements for location '{loc.get('name')}': {len(sensor_data)}")
            if len(sensor_data) >= required_sensor_count:
                candidate_locations.append({
                    "location": loc,
                    "sensor_measurements": sensor_data
                })
            break  # Exit loop early since we only need CJ-3

    if candidate_locations:
        candidate_locations.sort(key=lambda x: x["location"]["distance"])
        chosen = candidate_locations[0]
    else:
        print("No location found with sufficient sensor data.")
        return

    # Structure output
    output = {
        "input_coordinates": {"lat": lat, "lon": lon},
        "selected_location": {
            "location_id": chosen["location"].get("id"),
            "name": chosen["location"].get("name"),
            "locality": chosen["location"].get("locality"),
            "distance_m": chosen["location"].get("distance"),
            "coordinates": chosen["location"].get("coordinates")
        },
        "sensor_measurements": chosen["sensor_measurements"]
    }

    json_filename = "latest_air_quality_data.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved structured air quality data to '{json_filename}'.")

    # Plot the sensor measurements for the chosen location
    plot_sensor_measurements(chosen["sensor_measurements"])


if __name__ == "__main__":
    main()
