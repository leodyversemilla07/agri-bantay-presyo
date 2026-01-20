"""
Tests for API endpoints.
"""


class TestCommoditiesAPI:
    """Tests for /api/v1/commodities endpoints."""

    def test_list_commodities_empty(self, client):
        """Test listing commodities when database is empty."""
        response = client.get("/api/v1/commodities/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_commodities(self, client, sample_commodity):
        """Test listing commodities."""
        response = client.get("/api/v1/commodities/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_commodity.name

    def test_create_commodity(self, client):
        """Test creating a new commodity."""
        response = client.post("/api/v1/commodities/", json={"name": "Tilapia", "category": "Fish", "unit": "kg"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tilapia"
        assert data["category"] == "Fish"
        assert "id" in data

    def test_create_duplicate_commodity(self, client, sample_commodity):
        """Test creating a duplicate commodity returns error."""
        response = client.post("/api/v1/commodities/", json={"name": sample_commodity.name, "category": "Rice"})
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

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
        response = client.get(f"/api/v1/commodities/search/{sample_commodity.name[:4]}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_filter_by_category(self, client, sample_commodity):
        """Test filtering commodities by category."""
        response = client.get(f"/api/v1/commodities/?category={sample_commodity.category}")
        assert response.status_code == 200
        data = response.json()
        assert all(c["category"] == sample_commodity.category for c in data)


class TestMarketsAPI:
    """Tests for /api/v1/markets endpoints."""

    def test_list_markets_empty(self, client):
        """Test listing markets when database is empty."""
        response = client.get("/api/v1/markets/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_markets(self, client, sample_market):
        """Test listing markets."""
        response = client.get("/api/v1/markets/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_market.name

    def test_create_market(self, client):
        """Test creating a new market."""
        response = client.post("/api/v1/markets/", json={"name": "Divisoria Market", "region": "NCR", "city": "Manila"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Divisoria Market"

    def test_create_duplicate_market(self, client, sample_market):
        """Test creating a duplicate market returns error."""
        response = client.post("/api/v1/markets/", json={"name": sample_market.name, "region": "NCR"})
        assert response.status_code == 400

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
        response = client.get(f"/api/v1/markets/search/{sample_market.name[:4]}")
        assert response.status_code == 200


class TestPricesAPI:
    """Tests for /api/v1/prices endpoints."""

    def test_get_daily_prices_empty(self, client):
        """Test getting daily prices when database is empty."""
        response = client.get("/api/v1/prices/daily")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_daily_prices(self, client, sample_price_entry):
        """Test getting daily prices."""
        response = client.get("/api/v1/prices/daily")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_daily_prices_by_date(self, client, sample_price_entry):
        """Test getting prices for a specific date."""
        response = client.get(f"/api/v1/prices/daily?report_date={sample_price_entry.report_date}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

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
        response = client.get(f"/api/v1/trends/history/{str(sample_commodity.id)}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestViewsAPI:
    """Tests for HTML view endpoints."""

    def test_home_page(self, client):
        """Test home page renders."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_markets_page(self, client):
        """Test markets page renders."""
        response = client.get("/markets")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_analytics_page(self, client):
        """Test analytics page renders."""
        response = client.get("/analytics")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
