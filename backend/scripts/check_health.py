import requests
try:
    resp = requests.get("http://localhost:8000/api/v1/stats/dashboard")
    print(f"Status: {resp.status_code}")
    print(f"Data: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")
