import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

mock_farmers = [
    {"farmer_id": "FARM_A", "latitude": 19.87, "longitude": 75.34, "acres": 3.0, "soil_profile": [95, 40, 120, 6.5, 850], "phone_number": "9876543210"},
    {"farmer_id": "FARM_B", "latitude": 19.89, "longitude": 75.36, "acres": 2.5, "soil_profile": [93, 41, 118, 6.4, 840], "phone_number": "9876543211"},
    {"farmer_id": "FARM_C", "latitude": 19.86, "longitude": 75.32, "acres": 4.0, "soil_profile": [96, 39, 122, 6.6, 860], "phone_number": "9876543212"},
    {"farmer_id": "FARM_D", "latitude": 19.88, "longitude": 75.35, "acres": 2.0, "soil_profile": [94, 40, 121, 6.5, 855], "phone_number": "9876543213"},
    {"farmer_id": "FARM_OUTLIER", "latitude": 21.14, "longitude": 79.08, "acres": 5.0, "soil_profile": [95, 40, 120, 6.5, 850], "phone_number": "9876543214"}
]

print("1. Injecting structured farmer streams over the network...")
for farmer in mock_farmers:
    res = requests.post(f"{BASE_URL}/v1/advisory/async", json=farmer)
    if res.status_code != 200:
        print(f"Error feeding data stream for {farmer['farmer_id']}. Code: {res.status_code}")
        exit()

time.sleep(1.5) # Allow background operations to settle

print("\n2. Fetching calculated Geospatial Procurement Hubs for logistics operators...")
hub_res = requests.get(f"{BASE_URL}/v1/logistics/hubs")

# FIX: Inspect response content metadata types safely before running JSON parser transformations
if hub_res.status_code == 200:
    try:
        print(json.dumps(hub_res.json(), indent=2))
    except Exception as e:
        print(f"Failed to parse JSON string response: {e}")
else:
    print(f"Server Error Flagged! Status Code: {hub_res.status_code}")
    print("--- RAW SERVER RESPONSE CONTENT TRACEBACK ---")
    print(hub_res.text)
    print("---------------------------------------------")
