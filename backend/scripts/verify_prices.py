import requests
try:
    print("Testing /prices/daily endpoint...")
    resp = requests.get("http://localhost:8000/api/v1/prices/daily")
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Found {len(data)} price entries.")
        if len(data) > 0:
            print(f"Sample: {data[0]['commodity']['name']} at {data[0]['price_prevailing']}")
    else:
        print(f"Failed: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
