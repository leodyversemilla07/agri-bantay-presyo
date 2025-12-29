import requests
try:
    print("Testing /markets endpoint...")
    resp = requests.get("http://localhost:8000/api/v1/markets")
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Found {len(data)} markets.")
    else:
        print(f"Failed: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
