"""
Tests for API endpoints.
"""


class TestCommoditiesAPI:
    """Tests for /api/v1/commodities endpoints."""

    def test_list_commodities_empty(self, client):
        """Test listing commodities when database is empty."""
        response = client.get("/api/v1/commodities/")
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0, "skip": 0, "limit": 100}

    def test_list_commodities(self, client, sample_commodity):
        """Test listing commodities."""
        response = client.get("/api/v1/commodities/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == sample_commodity.name

    def test_create_commodity(self, client, auth_headers):
        """Test creating a new commodity."""
        response = client.post(
            "/api/v1/commodities/",
            json={"name": "Tilapia", "category": "Fish", "unit": "kg"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tilapia"
        assert data["category"] == "Fish"
        assert "id" in data
        assert response.headers["location"].endswith(f"/api/v1/commodities/{data['id']}")

    def test_create_duplicate_commodity(self, client, sample_commodity, auth_headers):
        """Test creating a duplicate commodity returns error."""
        response = client.post(
            "/api/v1/commodities/",
            json={"name": sample_commodity.name, "category": "Rice"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_commodity_requires_api_key(self, client):
        """Test creating a commodity without an API key is rejected."""
        response = client.post("/api/v1/commodities/", json={"name": "Tilapia", "category": "Fish", "unit": "kg"})
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"

    def test_create_commodity_rejects_invalid_api_key(self, client):
        """Test creating a commodity with an invalid API key is rejected."""
        response = client.post(
            "/api/v1/commodities/",
            json={"name": "Tilapia", "category": "Fish", "unit": "kg"},
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid API key"

    def test_create_commodity_fails_when_server_has_no_api_key(self, client):
        """Test creating a commodity fails explicitly if the server key is not configured."""
        from app.core.config import settings

        original_api_key = settings.API_KEY
        settings.API_KEY = None
        try:
            response = client.post(
                "/api/v1/commodities/",
                json={"name": "Tilapia", "category": "Fish", "unit": "kg"},
                headers={"X-API-Key": "anything"},
            )
        finally:
            settings.API_KEY = original_api_key

        assert response.status_code == 503
        assert response.json()["detail"] == "API key authentication is not configured on the server"

    def test_get_commodity_by_id(self, client, sample_commodity):
        """Test retrieving a commodity by ID."""
        response = client.get(f"/api/v1/commodities/{str(sample_commodity.id)}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_commodity.name

    def test_get_commodity_not_found(self, client):
        """Test retrieving a non-existent commodity."""
        response = client.get("/api/v1/commodities/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_search_commodities(self, client, sample_commodity):
        """Test searching commodities."""
        response = client.get(f"/api/v1/commodities/?q={sample_commodity.name[:4]}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    def test_filter_by_category(self, client, sample_commodity):
        """Test filtering commodities by category."""
        response = client.get(f"/api/v1/commodities/?category={sample_commodity.category}")
        assert response.status_code == 200
        data = response.json()
        assert all(c["category"] == sample_commodity.category for c in data["items"])


class TestMarketsAPI:
    """Tests for /api/v1/markets endpoints."""

    def test_list_markets_empty(self, client):
        """Test listing markets when database is empty."""
        response = client.get("/api/v1/markets/")
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0, "skip": 0, "limit": 100}

    def test_list_markets(self, client, sample_market):
        """Test listing markets."""
        response = client.get("/api/v1/markets/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == sample_market.name

    def test_create_market(self, client, auth_headers):
        """Test creating a new market."""
        response = client.post(
            "/api/v1/markets/",
            json={"name": "Divisoria Market", "region": "NCR", "city": "Manila"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Divisoria Market"
        assert response.headers["location"].endswith(f"/api/v1/markets/{data['id']}")

    def test_create_duplicate_market(self, client, sample_market, auth_headers):
        """Test creating a duplicate market returns error."""
        response = client.post(
            "/api/v1/markets/",
            json={"name": sample_market.name, "region": "NCR"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_create_market_requires_api_key(self, client):
        """Test creating a market without an API key is rejected."""
        response = client.post("/api/v1/markets/", json={"name": "Divisoria Market", "region": "NCR", "city": "Manila"})
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"

    def test_get_market_by_id(self, client, sample_market):
        """Test retrieving a market by ID."""
        response = client.get(f"/api/v1/markets/{str(sample_market.id)}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_market.name

    def test_get_market_not_found(self, client):
        """Test retrieving a non-existent market."""
        response = client.get("/api/v1/markets/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_search_markets(self, client, sample_market):
        """Test searching markets."""
        response = client.get(f"/api/v1/markets/?q={sample_market.name[:4]}")
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1


class TestPricesAPI:
    """Tests for /api/v1/prices endpoints."""

    def test_get_daily_prices_empty(self, client):
        """Test getting daily prices when database is empty."""
        response = client.get("/api/v1/prices/")
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0, "skip": 0, "limit": 100}

    def test_get_daily_prices(self, client, sample_price_entry):
        """Test getting daily prices."""
        response = client.get("/api/v1/prices/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["period_start"] == "2025-01-01"
        assert data["items"][0]["period_end"] == "2025-01-15"

    def test_get_daily_prices_by_date(self, client, sample_price_entry):
        """Test getting prices for a specific date."""
        response = client.get(f"/api/v1/prices/?report_date={sample_price_entry.report_date}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    def test_export_prices_csv(self, client, sample_price_entry):
        """Test exporting prices as CSV."""
        response = client.get("/api/v1/prices/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Commodity" in response.text


class TestStatsAPI:
    """Tests for /api/v1/stats endpoints."""

    def test_dashboard_stats_empty(self, client):
        """Test dashboard stats when database is empty."""
        response = client.get("/api/v1/stats/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["commodities"]["count"] == 0
        assert data["markets"]["count"] == 0
        assert data["prices"]["count"] == 0

    def test_dashboard_stats(self, client, sample_price_entry):
        """Test dashboard stats with data."""
        response = client.get("/api/v1/stats/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["commodities"]["count"] == 1
        assert data["markets"]["count"] == 1
        assert data["prices"]["count"] == 1


class TestTrendsAPI:
    """Tests for /api/v1/trends endpoints."""

    def test_commodity_history(self, client, sample_price_entry, sample_commodity):
        """Test getting commodity price history."""
        response = client.get(f"/api/v1/commodities/{str(sample_commodity.id)}/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_legacy_commodity_history_alias(self, client, sample_price_entry, sample_commodity):
        """Test the legacy commodity history alias still works."""
        response = client.get(f"/api/v1/trends/history/{str(sample_commodity.id)}")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestMetaAPI:
    """Tests for API metadata endpoints."""

    def test_root_endpoint(self, client):
        """Test the service root returns API metadata."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "rest-api"
        assert data["api_base_url"] == "/api/v1"
        assert data["docs_url"] == "/docs"

    def test_health_endpoint(self, client):
        """Test the health endpoint returns ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_html_routes_not_exposed(self, client):
        """Test legacy HTML routes are no longer exposed."""
        assert client.get("/markets").status_code == 404
        assert client.get("/analytics").status_code == 404
