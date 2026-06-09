import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000/v1/advisory/async"

def generate_random_farmer_payload(index: int) -> dict:
    """
    Generates a mix of valid and intentionally corrupt payloads to test
    if the API can successfully filter out bad inputs under heavy load.
    """
    is_valid = random.choice([True, True, False]) # 66% valid, 33% invalid data
    
    if is_valid:
        # Valid bounds for testing the successful pipeline path
        lat = round(random.uniform(19.0, 23.0), 4)
        lon = round(random.uniform(73.0, 78.0), 4)
        n = round(random.uniform(30, 130), 1)
        p = round(random.uniform(15, 80), 1)
        k = round(random.uniform(20, 180), 1)
        ph = round(random.uniform(5.8, 7.8), 1)
        rainfall = round(random.uniform(500, 1100), 1)
        phone = f"+91{random.randint(7000000000, 9999999999)}"
    else:
        # Intentionally invalid values to stress-test your validation layer
        lat = round(random.uniform(0.0, 5.0), 4)        # Out of bounds for India
        lon = round(random.uniform(100.0, 120.0), 4)    # Out of bounds for India
        n = round(random.uniform(500, 1000), 1)         # Too high
        p = round(random.uniform(-50, -10), 1)          # Negative values
        k = round(random.uniform(600, 900), 1)          # Too high
        ph = round(random.uniform(11.0, 14.0), 1)       # Barren soil scale
        rainfall = round(random.uniform(5000, 9000), 1) # Unrealistically high
        phone = "invalid_phone_123"                     # Bad format string

    return {
        "farmer_id": f"STRESS_FARM_{index:04d}",
        "latitude": lat,
        "longitude": lon,
        "acres": round(random.uniform(1.0, 10.0), 1),
        "soil_profile": [n, p, k, ph, rainfall],
        "phone_number": phone
    }

def send_api_request(payload: dict) -> int:
    """Sends a single POST request and logs the resulting HTTP status code."""
    try:
        response = requests.post(BASE_URL, json=payload, timeout=5)
        return response.status_code
    except requests.exceptions.RequestException:
        return 500 # Flags network connection timeouts

def execute_load_test(total_requests: int = 150, max_workers: int = 15):
    print(f"🚀 Starting Stress Test: Firing {total_requests} requests using {max_workers} concurrent threads...\n")
    
    # Pre-generate our array of varied payloads
    payloads = [generate_random_farmer_payload(i) for i in range(total_requests)]
    
    start_time = time.time()
    results = []
    
    # Execute network requests in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(send_api_request, p): p for p in payloads}
        for future in as_completed(futures):
            results.append(future.result())
            
    elapsed_time = time.time() - start_time
    
    # Parse status logs
    success_count = results.count(200)
    validation_blocked_count = results.count(422)
    server_error_count = results.count(500)
    
    print("================ STRESS TEST SUMMARY ================")
    print(f"Total Requests Dispatched   : {total_requests}")
    print(f"Execution Time              : {elapsed_time:.2f} seconds")
    print(f"Throughput Rate             : {total_requests / elapsed_time:.2f} req/sec")
    print("-----------------------------------------------------")
    print(f"✅ Queued Successfully (200) : {success_count} requests")
    print(f"🛡️  Blocked by Validation (422): {validation_blocked_count} requests")
    print(f"❌ Server / Timeout Error (500) : {server_error_count} requests")
    print("=====================================================")

if __name__ == "__main__":
    execute_load_test()
