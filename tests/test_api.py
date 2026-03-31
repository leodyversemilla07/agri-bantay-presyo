"""
Tests for API endpoints.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry


def _add_price(db_session, commodity_id, market_id, report_date, price_prevailing):
    entry = PriceEntry(
        commodity_id=commodity_id,
        market_id=market_id,
        report_date=report_date,
        price_prevailing=Decimal(price_prevailing),
        report_type="DAILY_RETAIL",
    )
    db_session.add(entry)
    return entry


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

    def test_create_duplicate_commodity_case_insensitive(self, client, sample_commodity, auth_headers):
        """Test creating a duplicate commodity with different case returns error."""
        response = client.post(
            "/api/v1/commodities/",
            json={"name": sample_commodity.name.lower(), "category": "Rice"},
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
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API key"

    def test_create_commodity_accepts_admin_api_key(self, client, admin_auth_headers):
        """Test admin credentials can access service-scoped write routes."""
        response = client.post(
            "/api/v1/commodities/",
            json={"name": "Tilapia", "category": "Fish", "unit": "kg"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 201

    def test_create_commodity_fails_when_server_has_no_api_key(self, client):
        """Test creating a commodity fails explicitly if the server key is not configured."""
        from app.core.config import settings

        original_api_key = settings.API_KEY
        original_service_api_keys = dict(settings.SERVICE_API_KEYS)
        original_admin_api_keys = dict(settings.ADMIN_API_KEYS)
        settings.API_KEY = None
        settings.SERVICE_API_KEYS = {}
        settings.ADMIN_API_KEYS = {}
        try:
            response = client.post(
                "/api/v1/commodities/",
                json={"name": "Tilapia", "category": "Fish", "unit": "kg"},
                headers={"X-API-Key": "anything"},
            )
        finally:
            settings.API_KEY = original_api_key
            settings.SERVICE_API_KEYS = original_service_api_keys
            settings.ADMIN_API_KEYS = original_admin_api_keys

        assert response.status_code == 503
        assert response.json()["detail"] == "Protected endpoint authentication is not configured on the server"

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

    def test_get_commodity_invalid_uuid(self, client):
        """Test malformed commodity IDs return a validation error."""
        response = client.get("/api/v1/commodities/not-a-uuid")
        assert response.status_code == 422

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

    def test_get_commodity_history_invalid_uuid(self, client):
        """Test malformed commodity IDs on history routes return a validation error."""
        response = client.get("/api/v1/commodities/not-a-uuid/history")
        assert response.status_code == 422


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

    def test_create_duplicate_market_case_insensitive(self, client, sample_market, auth_headers):
        """Test creating a duplicate market with different case returns error."""
        response = client.post(
            "/api/v1/markets/",
            json={"name": sample_market.name.lower(), "region": "NCR"},
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

    def test_get_market_invalid_uuid(self, client):
        """Test malformed market IDs return a validation error."""
        response = client.get("/api/v1/markets/not-a-uuid")
        assert response.status_code == 422

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

    def test_get_daily_prices_defaults_to_latest_snapshot(self, client, db_session, sample_price_entry):
        """Test latest prices without a date only returns the latest report snapshot."""
        latest_entry = PriceEntry(
            commodity_id=sample_price_entry.commodity_id,
            market_id=sample_price_entry.market_id,
            report_date=date(2025, 1, 20),
            price_prevailing=Decimal("60.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(latest_entry)
        db_session.commit()

        response = client.get("/api/v1/prices/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["report_date"] == "2025-01-20"

    def test_export_prices_csv(self, client, sample_price_entry):
        """Test exporting prices as CSV."""
        response = client.get("/api/v1/prices/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Commodity" in response.text

    def test_export_prices_csv_defaults_to_latest_snapshot(self, client, db_session, sample_price_entry):
        """Test CSV export without a date only exports the latest report snapshot."""
        latest_entry = PriceEntry(
            commodity_id=sample_price_entry.commodity_id,
            market_id=sample_price_entry.market_id,
            report_date=date(2025, 1, 20),
            price_prevailing=Decimal("60.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(latest_entry)
        db_session.commit()

        response = client.get("/api/v1/prices/export")
        assert response.status_code == 200
        assert "2025-01-20" in response.text
        assert "2025-01-15" not in response.text

    def test_get_daily_prices_filters_by_commodity_latest_within_slice(
        self, client, db_session, sample_commodity, sample_market
    ):
        """Test commodity filters still default to the latest snapshot within the filtered slice."""
        other_commodity = Commodity(id=uuid4(), name="Filtered Banana", category="Fruit", unit="kg")
        db_session.add(other_commodity)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, other_commodity.id, sample_market.id, date(2025, 1, 15), "80.00")
        db_session.commit()

        response = client.get(f"/api/v1/prices/?commodity_id={other_commodity.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["commodity_id"] == str(other_commodity.id)
        assert data["items"][0]["report_date"] == "2025-01-15"

    def test_get_daily_prices_filters_by_category_and_region(self, client, db_session, sample_commodity, sample_market):
        """Test category and region filters are supported on the price API."""
        other_commodity = Commodity(id=uuid4(), name="Filtered Banana", category="Fruit", unit="kg")
        other_market = Market(id=uuid4(), name="South Market", region="Region IV-A", city="Calamba")
        db_session.add_all([other_commodity, other_market])

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, other_commodity.id, other_market.id, date(2025, 1, 20), "80.00")
        db_session.commit()

        response = client.get("/api/v1/prices/?category=fruit&region=region%20iv-a")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["commodity"]["name"] == "Filtered Banana"
        assert data["items"][0]["market"]["region"] == "Region IV-A"

    def test_get_daily_prices_filters_by_date_range(self, client, db_session, sample_commodity, sample_market):
        """Test historical date-range queries are inclusive."""
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 18), "110.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "120.00")
        db_session.commit()

        response = client.get("/api/v1/prices/?start_date=2025-01-15&end_date=2025-01-18")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert [item["report_date"] for item in data["items"]] == ["2025-01-18", "2025-01-15"]

    def test_get_daily_prices_rejects_invalid_date_combinations(self, client):
        """Test mutually exclusive date modes are rejected."""
        response = client.get("/api/v1/prices/?report_date=2025-01-20&start_date=2025-01-15")
        assert response.status_code == 422

        response = client.get("/api/v1/prices/?start_date=2025-01-20&end_date=2025-01-15")
        assert response.status_code == 422

    def test_get_daily_prices_invalid_filter_uuid(self, client):
        """Test malformed filter UUIDs return validation errors."""
        response = client.get("/api/v1/prices/?commodity_id=not-a-uuid")
        assert response.status_code == 422

    def test_export_prices_csv_respects_filters_and_range_filename(
        self, client, db_session, sample_commodity, sample_market
    ):
        """Test CSV export uses the same filters and range filename semantics as /prices."""
        other_commodity = Commodity(id=uuid4(), name="Filtered Banana", category="Fruit", unit="kg")
        db_session.add(other_commodity)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, other_commodity.id, sample_market.id, date(2025, 1, 18), "80.00")
        _add_price(db_session, other_commodity.id, sample_market.id, date(2025, 1, 20), "90.00")
        db_session.commit()

        response = client.get(
            f"/api/v1/prices/export?commodity_id={other_commodity.id}&start_date=2025-01-18&end_date=2025-01-20"
        )
        assert response.status_code == 200
        assert 'filename=prices_2025-01-18_to_2025-01-20.csv' in response.headers["content-disposition"]
        assert "Filtered Banana" in response.text
        assert "2025-01-18" in response.text
        assert "2025-01-20" in response.text
        assert "Test Rice" not in response.text

    def test_get_daily_prices_supports_compact_view(self, client, db_session, sample_commodity, sample_market):
        """Test compact view returns flat price items."""
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        db_session.commit()

        response = client.get("/api/v1/prices/?view=compact")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["commodity_name"] == "Test Rice"
        assert data["items"][0]["market_name"] == "Test Market"
        assert "commodity" not in data["items"][0]
        assert "market" not in data["items"][0]

    def test_get_daily_prices_sorts_by_commodity_name(self, client, db_session, sample_market):
        """Test sorting by commodity name is supported."""
        rice = Commodity(id=uuid4(), name="Rice", category="Grain", unit="kg")
        banana = Commodity(id=uuid4(), name="Banana", category="Fruit", unit="kg")
        db_session.add_all([rice, banana])

        _add_price(db_session, rice.id, sample_market.id, date(2025, 1, 20), "100.00")
        _add_price(db_session, banana.id, sample_market.id, date(2025, 1, 20), "80.00")
        db_session.commit()

        response = client.get("/api/v1/prices/?sort_by=commodity_name&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert [item["commodity"]["name"] for item in data["items"]] == ["Banana", "Rice"]

    def test_get_daily_prices_sorts_by_prevailing_price(self, client, db_session, sample_commodity, sample_market):
        """Test sorting by prevailing price uses ascending or descending ordering."""
        second_commodity = Commodity(id=uuid4(), name="Filtered Banana", category="Fruit", unit="kg")
        db_session.add(second_commodity)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 20), "80.00")
        db_session.commit()

        response = client.get("/api/v1/prices/?sort_by=prevailing_price&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert [item["commodity"]["name"] for item in data["items"]] == ["Filtered Banana", "Test Rice"]

    def test_get_daily_prices_rejects_invalid_view_and_sort_params(self, client):
        """Test invalid sort and view params return validation errors."""
        response = client.get("/api/v1/prices/?view=summary")
        assert response.status_code == 422

        response = client.get("/api/v1/prices/?sort_by=price_low")
        assert response.status_code == 422

        response = client.get("/api/v1/prices/?sort_order=sideways")
        assert response.status_code == 422

    def test_export_prices_csv_respects_sort_order(self, client, db_session, sample_market):
        """Test CSV export uses the same sorting contract as /prices."""
        rice = Commodity(id=uuid4(), name="Rice", category="Grain", unit="kg")
        banana = Commodity(id=uuid4(), name="Banana", category="Fruit", unit="kg")
        db_session.add_all([rice, banana])

        _add_price(db_session, rice.id, sample_market.id, date(2025, 1, 20), "100.00")
        _add_price(db_session, banana.id, sample_market.id, date(2025, 1, 20), "80.00")
        db_session.commit()

        response = client.get("/api/v1/prices/export?sort_by=commodity_name&sort_order=asc")
        assert response.status_code == 200
        lines = response.text.splitlines()
        assert '"Banana"' in lines[1]
        assert '"Rice"' in lines[2]


class TestStatsAPI:
    """Tests for /api/v1/stats endpoints."""

    def test_dashboard_stats_empty(self, client):
        """Test dashboard stats when database is empty."""
        response = client.get("/api/v1/stats/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["latest_report_date"] is None
        assert data["previous_report_date"] is None
        assert data["commodities"]["count"] == 0
        assert data["commodities"]["change"] is None
        assert data["markets"]["count"] == 0
        assert data["markets"]["change"] is None
        assert data["prices"]["count"] == 0
        assert data["prices"]["change"] is None

    def test_dashboard_stats(self, client, sample_price_entry):
        """Test dashboard stats with data."""
        response = client.get("/api/v1/stats/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["latest_report_date"] == "2025-01-15"
        assert data["previous_report_date"] is None
        assert data["commodities"]["count"] == 1
        assert data["commodities"]["change"] is None
        assert data["markets"]["count"] == 1
        assert data["markets"]["change"] is None
        assert data["prices"]["count"] == 1
        assert data["prices"]["change"] is None

    def test_dashboard_stats_prices_count_latest_snapshot_only(self, client, db_session, sample_price_entry):
        """Test dashboard price count only reflects the latest report snapshot."""
        latest_entry = PriceEntry(
            commodity_id=sample_price_entry.commodity_id,
            market_id=sample_price_entry.market_id,
            report_date=date(2025, 1, 20),
            price_prevailing=Decimal("60.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(latest_entry)
        db_session.commit()

        response = client.get("/api/v1/stats/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["latest_report_date"] == "2025-01-20"
        assert data["prices"]["count"] == 1

    def test_dashboard_stats_includes_real_snapshot_deltas(self, client, db_session, sample_commodity, sample_market):
        """Test dashboard deltas compare against the previous available snapshot."""
        extra_commodity = Commodity(id=uuid4(), name="Test Onion", category="Vegetable", unit="kg")
        extra_market = Market(id=uuid4(), name="North Market", region="NCR", city="Quezon City")
        db_session.add_all([extra_commodity, extra_market])

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "110.00")
        _add_price(db_session, extra_commodity.id, extra_market.id, date(2025, 1, 20), "80.00")
        db_session.commit()

        response = client.get("/api/v1/stats/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["latest_report_date"] == "2025-01-20"
        assert data["previous_report_date"] == "2025-01-15"
        assert data["commodities"]["change"] == 1
        assert data["markets"]["change"] == 1
        assert data["prices"]["change"] == 1


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

    def test_legacy_commodity_history_invalid_uuid(self, client):
        """Test malformed commodity IDs on the legacy history route return a validation error."""
        response = client.get("/api/v1/trends/history/not-a-uuid")
        assert response.status_code == 422

    def test_commodity_trend_summary_aggregated(self, client, db_session, sample_commodity, sample_market):
        """Test aggregated commodity trend summary uses market averages."""
        second_market = Market(id=uuid4(), name="South Market", region="NCR", city="Makati")
        db_session.add(second_market)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        response = client.get(f"/api/v1/trends/commodities/{sample_commodity.id}/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["latest_report_date"] == "2025-01-20"
        assert data["previous_report_date"] == "2025-01-15"
        assert data["current_prevailing_price"] == "140.00"
        assert data["previous_prevailing_price"] == "110.00"
        assert data["absolute_change"] == "30.00"
        assert data["percent_change"] == 27.3
        assert data["market_count"] == 2

    def test_commodity_trend_summary_for_specific_market(self, client, db_session, sample_commodity, sample_market):
        """Test market-specific summary uses only the requested market."""
        second_market = Market(id=uuid4(), name="South Market", region="NCR", city="Makati")
        db_session.add(second_market)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        response = client.get(f"/api/v1/trends/commodities/{sample_commodity.id}/summary?market_id={sample_market.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["current_prevailing_price"] == "130.00"
        assert data["previous_prevailing_price"] == "100.00"
        assert data["absolute_change"] == "30.00"
        assert data["percent_change"] == 30.0
        assert data["market_count"] == 1

    def test_commodity_trend_summary_invalid_market_id(self, client, sample_commodity):
        """Test malformed market IDs on trend summary return a validation error."""
        response = client.get(f"/api/v1/trends/commodities/{sample_commodity.id}/summary?market_id=not-a-uuid")
        assert response.status_code == 422

    def test_commodity_trend_summary_not_found(self, client, sample_commodity):
        """Test summary returns 404 when the commodity has no price history."""
        response = client.get(f"/api/v1/trends/commodities/{sample_commodity.id}/summary")
        assert response.status_code == 404

    def test_commodity_trend_series_returns_points(self, client, db_session, sample_commodity, sample_market):
        """Test trend series returns chronological aggregated points."""
        second_market = Market(id=uuid4(), name="South Market", region="NCR", city="Makati")
        db_session.add(second_market)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 18), "110.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 18), "130.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        response = client.get(f"/api/v1/trends/commodities/{sample_commodity.id}/series?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["points"]) == 2
        assert data["points"][0]["report_date"] == "2025-01-18"
        assert data["points"][1]["report_date"] == "2025-01-20"
        assert data["points"][1]["prevailing_price"] == "140.00"
        assert data["points"][1]["market_count"] == 2

    def test_market_trend_summary_aggregated(self, client, db_session, sample_commodity, sample_market):
        """Test aggregated market trend summary uses commodity averages."""
        second_commodity = Commodity(id=uuid4(), name="Filtered Banana", category="Fruit", unit="kg")
        db_session.add(second_commodity)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        response = client.get(f"/api/v1/trends/markets/{sample_market.id}/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["latest_report_date"] == "2025-01-20"
        assert data["previous_report_date"] == "2025-01-15"
        assert data["current_prevailing_price"] == "140.00"
        assert data["previous_prevailing_price"] == "110.00"
        assert data["absolute_change"] == "30.00"
        assert data["percent_change"] == 27.3
        assert data["commodity_count"] == 2

    def test_market_trend_summary_for_specific_commodity(self, client, db_session, sample_commodity, sample_market):
        """Test commodity-specific market summary uses only the requested commodity."""
        second_commodity = Commodity(id=uuid4(), name="Filtered Banana", category="Fruit", unit="kg")
        db_session.add(second_commodity)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        response = client.get(f"/api/v1/trends/markets/{sample_market.id}/summary?commodity_id={sample_commodity.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["current_prevailing_price"] == "130.00"
        assert data["previous_prevailing_price"] == "100.00"
        assert data["absolute_change"] == "30.00"
        assert data["percent_change"] == 30.0
        assert data["commodity_count"] == 1

    def test_market_trend_summary_invalid_commodity_id(self, client, sample_market):
        """Test malformed commodity IDs on market trend summary return a validation error."""
        response = client.get(f"/api/v1/trends/markets/{sample_market.id}/summary?commodity_id=not-a-uuid")
        assert response.status_code == 422

    def test_market_trend_summary_not_found(self, client, sample_market):
        """Test market summary returns 404 when the market has no price history."""
        response = client.get(f"/api/v1/trends/markets/{sample_market.id}/summary")
        assert response.status_code == 404

    def test_market_trend_series_returns_points(self, client, db_session, sample_commodity, sample_market):
        """Test market trend series returns chronological aggregated points."""
        second_commodity = Commodity(id=uuid4(), name="Filtered Banana", category="Fruit", unit="kg")
        db_session.add(second_commodity)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 18), "110.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 18), "130.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, second_commodity.id, sample_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        response = client.get(f"/api/v1/trends/markets/{sample_market.id}/series?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["points"]) == 2
        assert data["points"][0]["report_date"] == "2025-01-18"
        assert data["points"][1]["report_date"] == "2025-01-20"
        assert data["points"][1]["prevailing_price"] == "140.00"
        assert data["points"][1]["commodity_count"] == 2


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

    def test_readiness_endpoint_ready(self, client, monkeypatch):
        """Test the readiness endpoint returns 200 when dependencies are ready."""
        monkeypatch.setattr(
            "app.api.meta.get_readiness_status",
            lambda db: {
                "status": "ready",
                "checks": {"postgres": True, "redis": True, "schema_at_head": True},
                "schema": {"current_revision": "head", "head_revision": "head"},
            },
        )

        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_readiness_endpoint_not_ready(self, client, monkeypatch):
        """Test the readiness endpoint returns 503 when dependencies are not ready."""
        monkeypatch.setattr(
            "app.api.meta.get_readiness_status",
            lambda db: {
                "status": "not_ready",
                "checks": {"postgres": True, "redis": False, "schema_at_head": False},
                "schema": {"current_revision": "old", "head_revision": "head"},
            },
        )

        response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json()["status"] == "not_ready"

    def test_html_routes_not_exposed(self, client):
        """Test legacy HTML routes are no longer exposed."""
        assert client.get("/markets").status_code == 404
        assert client.get("/analytics").status_code == 404


class TestAdminAPI:
    """Tests for admin-only operational endpoints."""

    def test_list_ingestion_runs_requires_api_key(self, client):
        response = client.get("/api/v1/admin/ingestion-runs")
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"

    def test_list_ingestion_runs_rejects_service_scope(self, client, auth_headers):
        response = client.get("/api/v1/admin/ingestion-runs", headers=auth_headers)
        assert response.status_code == 403
        assert response.json()["detail"] == "Insufficient API key scope"

    def test_list_ingestion_runs_returns_recent_runs(self, client, db_session, admin_auth_headers):
        from app.models.ingestion_run import IngestionRun

        first = IngestionRun(
            task_name="discover_and_scrape",
            status="success",
            entries_total=1,
            entries_processed=1,
            anomaly_count=0,
            anomaly_flags=[],
            started_at=datetime(2025, 1, 20, 8, 0, 0, tzinfo=UTC).replace(tzinfo=None),
        )
        second = IngestionRun(
            task_name="scrape_daily_prices",
            status="partial_success",
            entries_total=100,
            entries_processed=98,
            entries_inserted=80,
            entries_updated=10,
            entries_skipped=8,
            error_count=2,
            anomaly_count=1,
            anomaly_flags=["duplicate_entries_in_source:2"],
            started_at=datetime(2025, 1, 20, 9, 0, 0, tzinfo=UTC).replace(tzinfo=None),
        )
        db_session.add_all([first, second])
        db_session.commit()

        response = client.get("/api/v1/admin/ingestion-runs", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["items"][0]["task_name"] == "scrape_daily_prices"
        assert data["items"][0]["anomaly_count"] == 1
        assert data["items"][0]["anomaly_flags"] == ["duplicate_entries_in_source:2"]
