"""
Tests for Pydantic schemas and validation.
"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.commodity import Commodity, CommodityCreate
from app.schemas.market import MarketCreate
from app.schemas.price_entry import PriceEntryCreate


class TestCommoditySchemas:
    """Tests for commodity schemas."""

    def test_commodity_create_valid(self):
        """Test valid commodity creation."""
        data = CommodityCreate(name="Bangus", category="Fish", variant="Fresh", unit="kg")
        assert data.name == "Bangus"
        assert data.category == "Fish"

    def test_commodity_create_minimal(self):
        """Test commodity creation with only required fields."""
        data = CommodityCreate(name="Rice")
        assert data.name == "Rice"
        assert data.category is None
        assert data.variant is None
        assert data.unit is None

    def test_commodity_create_missing_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            CommodityCreate()
        assert "name" in str(exc_info.value)

    def test_commodity_schema_from_orm(self):
        """Test Commodity schema with from_attributes."""

        # Simulate ORM object
        class FakeCommodity:
            id = uuid4()
            name = "Tilapia"
            category = "Fish"
            variant = None
            unit = "kg"

        commodity = Commodity.model_validate(FakeCommodity())
        assert commodity.name == "Tilapia"
        assert commodity.id is not None


class TestMarketSchemas:
    """Tests for market schemas."""

    def test_market_create_valid(self):
        """Test valid market creation."""
        data = MarketCreate(name="Divisoria Market", region="NCR", city="Manila")
        assert data.name == "Divisoria Market"
        assert data.region == "NCR"

    def test_market_create_minimal(self):
        """Test market creation with only required fields."""
        data = MarketCreate(name="Test Market")
        assert data.name == "Test Market"
        assert data.region is None
        assert data.is_regional_average is False

    def test_market_create_missing_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            MarketCreate()

    def test_market_is_regional_average_default(self):
        """Test default value for is_regional_average."""
        data = MarketCreate(name="NCR Average", is_regional_average=True)
        assert data.is_regional_average is True


class TestPriceEntrySchemas:
    """Tests for price entry schemas."""

    def test_price_entry_create_valid(self):
        """Test valid price entry creation."""
        data = PriceEntryCreate(
            commodity_id=uuid4(),
            market_id=uuid4(),
            report_date=date(2025, 1, 15),
            price_low=Decimal("45.00"),
            price_high=Decimal("55.00"),
            price_prevailing=Decimal("50.00"),
            report_type="DAILY_RETAIL",
        )
        assert data.price_prevailing == Decimal("50.00")
        assert data.report_type == "DAILY_RETAIL"

    def test_price_entry_minimal(self):
        """Test price entry with only required fields."""
        data = PriceEntryCreate(
            commodity_id=uuid4(), market_id=uuid4(), report_date=date(2025, 1, 15), report_type="DAILY_RETAIL"
        )
        assert data.price_low is None
        assert data.price_high is None

    def test_price_entry_missing_required(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            PriceEntryCreate(
                commodity_id=uuid4(),
                # Missing market_id, report_date, report_type
            )
        errors = str(exc_info.value)
        assert "market_id" in errors or "report_date" in errors

    def test_price_entry_decimal_precision(self):
        """Test decimal values are handled correctly."""
        data = PriceEntryCreate(
            commodity_id=uuid4(),
            market_id=uuid4(),
            report_date=date(2025, 1, 15),
            price_prevailing=Decimal("123.45"),
            report_type="DAILY_RETAIL",
        )
        assert data.price_prevailing == Decimal("123.45")

    def test_price_entry_with_optional_fields(self):
        """Test price entry with all optional fields."""
        data = PriceEntryCreate(
            commodity_id=uuid4(),
            market_id=uuid4(),
            report_date=date(2025, 1, 15),
            price_low=Decimal("40.00"),
            price_high=Decimal("60.00"),
            price_prevailing=Decimal("50.00"),
            price_average=Decimal("50.00"),
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 15),
            report_type="DAILY_RETAIL",
            source_file="test.pdf",
        )
        assert data.period_start == date(2025, 1, 1)
        assert data.source_file == "test.pdf"
