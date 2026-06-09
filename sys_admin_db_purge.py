import requests
import json

# The exact, complete address of your local FastAPI application server
BASE_URL = "http://127.0.0.1:8000"

def check_system_status():
    """Queries the live database to pull active ledger statistics."""
    try:
        response = requests.get(f"{BASE_URL}/v1/system/status")
        if response.status_code == 200:
            print("\n🟢 [SYSTEM ONLINE]")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n🔴 Server responded with error status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Is your Uvicorn API server currently running?")

def purge_database():
    """Triggers the secure programmatic database wipe endpoint over the network."""
    print("\n⚠️  Sending secure database purge request...")
    try:
        response = requests.post(f"{BASE_URL}/v1/system/purge")
        if response.status_code == 200:
            print("🧹 [PURGE SUCCESSFUL]")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Purge failed with status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the API server.")

if __name__ == "__main__":
    print("--- AgriIntel Platform Administrative Utility ---")
    
    # 1. Check status before the wipe
    print("\nChecking current system footprint:")
    check_system_status()
    
    # 2. Trigger the database reset
    purge_database()
    
    # 3. Verify that records dropped to 0
    print("\nVerifying final system footprint:")
    check_system_status()
