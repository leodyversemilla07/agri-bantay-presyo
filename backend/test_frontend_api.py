from fastapi.testclient import TestClient
from app.main import app
from app.services.commodity_service import CommodityService

client = TestClient(app)

def test_dashboard_endpoints():
    print("\n🔍 TESTING BACKEND ENDPOINTS FOR FRONTEND")
    
    # 1. Test Dashboard Stats
    print("\n1. Testing /stats/dashboard")
    resp = client.get("/api/v1/stats/dashboard")
    if resp.status_code == 200:
        print(f"✅ Success: {resp.json()}")
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")

    # 2. Test Commodities with Category Filter
    print("\n2. Testing /commodities?category=Rice")
    resp = client.get("/api/v1/commodities?category=Rice")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Success: Found {len(data)} items")
        if len(data) > 0:
            print(f"   Sample: {data[0]['name']} ({data[0]['category']})")
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")

    # 3. Test History for a Commodity
    # First get a commodity ID
    resp = client.get("/api/v1/commodities")
    if resp.status_code == 200 and len(resp.json()) > 0:
        comm_id = resp.json()[0]['id']
        print(f"\n3. Testing /trends/history/{comm_id}")
        resp = client.get(f"/api/v1/trends/history/{comm_id}")
        if resp.status_code == 200:
            hist = resp.json()
            print(f"✅ Success: Found {len(hist)} history entries")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
    else:
        print("⚠️ Skipping history test (no commodities found)")

if __name__ == "__main__":
    test_dashboard_endpoints()
