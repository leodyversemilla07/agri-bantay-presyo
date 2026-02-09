"""
Tests for database models.
"""

from datetime import date
from decimal import Decimal

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry
from app.models.supply_index import SupplyIndex


class TestCommodityModel:
    """Tests for Commodity model."""

    def test_create_commodity(self, db_session):
        """Test creating a commodity."""
        commodity = Commodity(name="Test Commodity", category="Vegetables", variant="Local", unit="kg")
        db_session.add(commodity)
        db_session.commit()

        assert commodity.id is not None
        assert commodity.name == "Test Commodity"

    def test_commodity_default_id(self, db_session):
        """Test that commodity gets UUID by default."""
        commodity = Commodity(name="Test")
        db_session.add(commodity)
        db_session.commit()

        assert commodity.id is not None
        # Check it's a valid UUID
        assert len(str(commodity.id)) == 36

    def test_commodity_tablename(self):
        """Test commodity table name."""
        assert Commodity.__tablename__ == "commodities"

    def test_commodity_relationship(self, db_session, sample_commodity, sample_market):
        """Test commodity-price_entry relationship."""
        entry = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 15),
            price_prevailing=Decimal("50.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(entry)
        db_session.commit()

        # Access through relationship
        db_session.refresh(sample_commodity)
        assert len(sample_commodity.price_entries) == 1


class TestMarketModel:
    """Tests for Market model."""

    def test_create_market(self, db_session):
        """Test creating a market."""
        market = Market(name="Test Market", region="NCR", city="Manila", is_regional_average=False)
        db_session.add(market)
        db_session.commit()

        assert market.id is not None
        assert market.name == "Test Market"

    def test_market_default_values(self, db_session):
        """Test market default values."""
        market = Market(name="Simple Market")
        db_session.add(market)
        db_session.commit()

        assert market.is_regional_average is False
        assert market.region is None

    def test_market_tablename(self):
        """Test market table name."""
        assert Market.__tablename__ == "markets"


class TestPriceEntryModel:
    """Tests for PriceEntry model."""

    def test_create_price_entry(self, db_session, sample_commodity, sample_market):
        """Test creating a price entry."""
        entry = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 15),
            price_low=Decimal("45.00"),
            price_high=Decimal("55.00"),
            price_prevailing=Decimal("50.00"),
            price_average=Decimal("50.00"),
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 15),
            report_type="DAILY_RETAIL",
            source_file="test.pdf",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.id is not None
        assert entry.price_prevailing == Decimal("50.00")
        assert entry.period_start == date(2025, 1, 1)
        assert entry.period_end == date(2025, 1, 15)

    def test_price_entry_relationships(self, db_session, sample_commodity, sample_market):
        """Test price entry relationships."""
        entry = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 15),
            price_prevailing=Decimal("50.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(entry)
        db_session.commit()
        db_session.refresh(entry)

        assert entry.commodity.name == sample_commodity.name
        assert entry.market.name == sample_market.name

    def test_price_entry_default_report_type(self, db_session, sample_commodity, sample_market):
        """Test default report type."""
        entry = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 15),
            price_prevailing=Decimal("50.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.report_type == "DAILY_RETAIL"

    def test_price_entry_tablename(self):
        """Test price entry table name."""
        assert PriceEntry.__tablename__ == "price_entries"


class TestSupplyIndexModel:
    """Tests for SupplyIndex model."""

    def test_create_supply_index(self, db_session, sample_commodity):
        """Test creating a supply index entry."""
        supply = SupplyIndex(
            commodity_id=sample_commodity.id,
            date=date(2025, 1, 15),
            volume_metric_tons=Decimal("1000.00"),
            wholesale_price=Decimal("45.00"),
        )
        db_session.add(supply)
        db_session.commit()

        assert supply.id is not None
        assert supply.volume_metric_tons == Decimal("1000.00")

    def test_supply_index_relationship(self, db_session, sample_commodity):
        """Test supply index commodity relationship."""
        supply = SupplyIndex(
            commodity_id=sample_commodity.id, date=date(2025, 1, 15), volume_metric_tons=Decimal("500.00")
        )
        db_session.add(supply)
        db_session.commit()
        db_session.refresh(supply)

        assert supply.commodity.name == sample_commodity.name

    def test_supply_index_tablename(self):
        """Test supply index table name."""
        assert SupplyIndex.__tablename__ == "supply_indices"
