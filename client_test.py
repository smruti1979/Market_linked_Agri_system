import requests

url = "http://127.0.0.1:8000/v1/advisory/async"

# Structural payload with soil data, coordinates, and phone routing target
#Invalid payload
# payload = {
#             "farmer_id": "FARM_ERR",
#             "latitude": 19.87,
#             "longitude": 75.34,
#             "soil_profile": [95.0, 40.0, 120.0, 13.5, 850.0],
#             "phone_number": "12345"
# }

# Valid payload
payload = {
            "farmer_id": "FARM_ERR",
            "latitude": 19.87,
            "longitude": 75.34,
            "soil_profile": [95.0, 40.0, 120.0, 9.5, 850.0],
            "phone_number": "9900383266"
}

print("Sending POST request to AgriIntel Async Pipeline...")
response = requests.post(url, json=payload)

print(f"Server Status Code: {response.status_code}")
print(f"Server Response Body: {response.json()}")
print("\nCheck your Uvicorn terminal window to view the background SMS generation logs!")
