import requests
import json
from datetime import datetime, timedelta, timezone
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Token from .env
API_KEY = os.getenv("openaq_token")

# -----------------------
# Configuration and API URLs
# -----------------------
BASE_URL = "https://api.openaq.org/v3"
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


# -----------------------
# Revised Measurement Retrieval Function with Date Range Filtering
# -----------------------
def get_latest_measurement_for_sensor(sensor_id, start_date, end_date):
    """
    Retrieve the most recent hourly measurement for the given sensor_id
    that falls between the provided ISO-formatted start_date and end_date.

    We call the /sensors/{sensor_id}/hours endpoint and then explicitly filter
    the returned measurements by the parsed timestamp.

    Example:
      start_date = "2025-02-01T00:00:00Z"
      end_date   = "2025-02-02T00:00:00Z"
    """
    url = f"{BASE_URL}/sensors/{sensor_id}/hours"
    params = {
        "date_from": start_date,
        "date_to": end_date,
        "limit": 1000,  # retrieve up to 100 hourly entries
        "order_by": "datetimeFrom.utc",
        "sort": "desc"
    }

    response = requests.get(url, headers=headers, params=params)
    print(f"Full Get_Latest_Hours API response for sensor {sensor_id}:")
    json_response = response.json()
    print(json_response)

    if response.status_code != 200:
        print(f"Error fetching data for sensor {sensor_id}: {response.status_code} {response.text}")
        return None

    results = json_response.get("results", [])
    if not results:
        print(f"No data returned for sensor {sensor_id} in the requested window.")
        return None

    # Convert provided ISO date strings to datetime objects.
    try:
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    except Exception as e:
        print(f"Error parsing supplied date range: {e}")
        return None

    # Filter results explicitly by the datetimeFrom value.
    valid_results = []
    for meas in results:
        dt_str = None
        period = meas.get("period", {})
        if isinstance(period.get("datetimeFrom"), dict):
            dt_str = period.get("datetimeFrom", {}).get("utc")
        elif isinstance(period.get("datetimeFrom"), str):
            dt_str = period.get("datetimeFrom")

        if dt_str:
            try:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except Exception as e:
                print(f"Error parsing datetime '{dt_str}' for sensor {sensor_id}: {e}")
                continue
            if start_dt <= dt <= end_dt:
                valid_results.append((dt, meas))

    if not valid_results:
        print(f"No measurement for sensor {sensor_id} falls within {start_date} to {end_date}.")
        return None

    # Select the measurement with the latest datetime among valid ones.
    latest_dt, latest_meas = max(valid_results, key=lambda x: x[0])
    print(f"Latest measurement for sensor {sensor_id}: {latest_meas}")
    return latest_meas


# -----------------------
# Process Location Function
# -----------------------
def process_location(location, start_date, end_date):
    """
    For a given location dictionary, iterate through its sensors and retrieve
    the hourly measurement (using get_latest_measurement_for_sensor) within the
    specified date range. Returns a list of sensor measurement entries.
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
        meas = get_latest_measurement_for_sensor(sensor_id, start_date, end_date)
        if meas:
            period = meas.get("period", {})
            measurement_datetime = None
            if isinstance(period.get("datetimeFrom"), dict):
                measurement_datetime = period.get("datetimeFrom", {}).get("utc")
            elif isinstance(period.get("datetimeFrom"), str):
                measurement_datetime = period.get("datetimeFrom")
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
            print(f"    No valid measurement found for sensor {sensor_id} in the date range.")
    return sensor_entries


# -----------------------
# Main Workflow
# -----------------------
def main():
    # CJ-3 location details.
    # Based on your Excel data, CJ-3 (location_id 2163127) has the following coordinates:
    #   latitude: 46.765425, longitude: 23.550258
    # Include all six sensors of interest:
    #   1. Sensor for "co µg/m³": 11438933
    #   2. Sensor for "no2 µg/m³": 9020849
    #   3. Sensor for "o3 µg/m³": 9020848
    #   4. Sensor for "pm10 µg/m³": 7774317
    #   5. Sensor for "pm25 µg/m³": 7773481
    #   6. Sensor for "so2 µg/m³": 7774375
    selected_location = {
        "id": 2163127,
        "name": "CJ-3",
        "coordinates": {"latitude": 46.765425, "longitude": 23.550258},
        "sensors": [
            {"id": 11438933, "name": "co µg/m³"},
            {"id": 9020849, "name": "no2 µg/m³"},
            {"id": 9020848, "name": "o3 µg/m³"},
            {"id": 7774317, "name": "pm10 µg/m³"},
            {"id": 7773481, "name": "pm25 µg/m³"},
            {"id": 7774375, "name": "so2 µg/m³"}
        ]
    }

    # Set the custom date range to match your Excel file.
    # For example: 2025-02-01T00:00:00Z to 2025-02-02T00:00:00Z.
    start_date = "2025-02-01T00:00:00Z"
    end_date = "2025-02-02T00:00:00Z"

    # Process the location using the custom date range.
    sensor_measurements = process_location(selected_location, start_date, end_date)

    # Structure the output.
    output = {
        "location": selected_location,
        "date_range": {"date_from": start_date, "date_to": end_date},
        "sensor_measurements": sensor_measurements
    }

    json_filename = "latest_air_quality_data.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved structured air quality data to '{json_filename}'.")

    # (Optional) Plotting code can be added here if desired.
    # plot_sensor_measurements(sensor_measurements)


if __name__ == "__main__":
    main()
