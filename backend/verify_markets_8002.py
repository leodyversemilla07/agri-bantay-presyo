import requests
try:
    print("Testing /markets endpoint on port 8002...")
    resp = requests.get("http://localhost:8002/api/v1/markets")
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Found {len(data)} markets.")
    else:
        print(f"Failed: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
