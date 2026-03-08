"""
Integration coverage for key API endpoints.
"""


def test_dashboard_endpoints(client, sample_price_entry, sample_commodity):
    stats_response = client.get("/api/v1/stats/dashboard")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["commodities"]["count"] == 1
    assert stats["markets"]["count"] == 1
    assert stats["prices"]["count"] == 1

    commodities_response = client.get("/api/v1/commodities?category=Rice")
    assert commodities_response.status_code == 200
    commodities = commodities_response.json()
    assert commodities["total"] == 1
    assert commodities["items"][0]["name"] == sample_commodity.name
    assert commodities["items"][0]["category"] == "Rice"

    history_response = client.get(f"/api/v1/commodities/{sample_commodity.id}/history")
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["report_date"] == "2025-01-15"
