"""
Unit tests for PriceService.
"""

from datetime import date, timedelta
from decimal import Decimal

from app.models.price_entry import PriceEntry
from app.services.price_service import PriceService


class TestPriceService:
    """Tests for PriceService methods."""

    def test_create_entry(self, db_session, sample_commodity, sample_market):
        """Test creating a new price entry."""
        data = {
            "commodity_id": sample_commodity.id,
            "market_id": sample_market.id,
            "report_date": date(2025, 1, 20),
            "price_low": Decimal("40.00"),
            "price_high": Decimal("50.00"),
            "price_prevailing": Decimal("45.00"),
            "price_average": Decimal("45.00"),
            "report_type": "DAILY_RETAIL",
            "source_file": "test.pdf",
        }

        result = PriceService.create_entry(db_session, data)

        assert result.id is not None
        assert result.price_prevailing == Decimal("45.00")
        assert result.commodity_id == sample_commodity.id

    def test_create_entry_upsert(self, db_session, sample_commodity, sample_market):
        """Test that create_entry updates existing entry instead of duplicating."""
        data = {
            "commodity_id": sample_commodity.id,
            "market_id": sample_market.id,
            "report_date": date(2025, 1, 20),
            "price_low": Decimal("40.00"),
            "price_high": Decimal("50.00"),
            "price_prevailing": Decimal("45.00"),
            "report_type": "DAILY_RETAIL",
        }

        # Create first entry
        entry1 = PriceService.create_entry(db_session, data)

        # Update with new price
        data["price_prevailing"] = Decimal("48.00")
        entry2 = PriceService.create_entry(db_session, data)

        # Should be same record, updated
        assert entry1.id == entry2.id
        assert entry2.price_prevailing == Decimal("48.00")

        # Verify only one record exists
        count = (
            db_session.query(PriceEntry)
            .filter(PriceEntry.commodity_id == sample_commodity.id, PriceEntry.report_date == date(2025, 1, 20))
            .count()
        )
        assert count == 1

    def test_get_latest_prices(self, db_session, sample_price_entry):
        """Test retrieving latest prices."""
        results = PriceService.get_latest_prices(db_session, skip=0, limit=10)

        assert len(results) == 1
        assert results[0].id == sample_price_entry.id

    def test_get_prices_by_date(self, db_session, sample_commodity, sample_market):
        """Test retrieving prices for a specific date."""
        target_date = date(2025, 1, 20)

        # Create entries for different dates
        for d in [date(2025, 1, 19), target_date, date(2025, 1, 21)]:
            entry = PriceEntry(
                commodity_id=sample_commodity.id,
                market_id=sample_market.id,
                report_date=d,
                price_prevailing=Decimal("50.00"),
                report_type="DAILY_RETAIL",
            )
            db_session.add(entry)
        db_session.commit()

        results = PriceService.get_prices_by_date(db_session, report_date=target_date)

        assert len(results) == 1
        assert results[0].report_date == target_date

    def test_get_commodity_history(self, db_session, sample_commodity, sample_market):
        """Test retrieving price history for a commodity."""
        # Create price entries for multiple dates
        base_date = date(2025, 1, 1)
        for i in range(10):
            entry = PriceEntry(
                commodity_id=sample_commodity.id,
                market_id=sample_market.id,
                report_date=base_date + timedelta(days=i),
                price_prevailing=Decimal("50.00") + i,
                report_type="DAILY_RETAIL",
            )
            db_session.add(entry)
        db_session.commit()

        # Convert UUID to string for SQLite compatibility
        results = PriceService.get_commodity_history(db_session, commodity_id=str(sample_commodity.id), limit=5)

        assert len(results) == 5
        # Should be ordered by date descending
        assert results[0].report_date > results[1].report_date

    def test_get_previous_price(self, db_session, sample_commodity, sample_market):
        """Test getting previous price for a commodity/market."""
        # Create two price entries
        entry1 = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 15),
            price_prevailing=Decimal("45.00"),
            report_type="DAILY_RETAIL",
        )
        entry2 = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 16),
            price_prevailing=Decimal("48.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        # Convert UUIDs to string for SQLite compatibility
        result = PriceService.get_previous_price(
            db_session,
            commodity_id=str(sample_commodity.id),
            market_id=str(sample_market.id),
            current_date=date(2025, 1, 16),
        )

        assert result is not None
        assert result.report_date == date(2025, 1, 15)
        assert result.price_prevailing == Decimal("45.00")

    def test_get_price_change(self, db_session, sample_commodity, sample_market):
        """Test calculating price change percentage."""
        # Create two price entries with known values
        entry1 = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 15),
            price_prevailing=Decimal("100.00"),
            report_type="DAILY_RETAIL",
        )
        entry2 = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 16),
            price_prevailing=Decimal("110.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        # Convert UUIDs to string for SQLite compatibility
        change = PriceService.get_price_change(
            db_session,
            commodity_id=str(sample_commodity.id),
            market_id=str(sample_market.id),
            current_date=date(2025, 1, 16),
        )

        # 10% increase: (110-100)/100 * 100 = 10.0
        assert change == 10.0

    def test_get_price_change_no_previous(self, db_session, sample_commodity, sample_market):
        """Test price change returns 0 when no previous price exists."""
        entry = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 15),
            price_prevailing=Decimal("50.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(entry)
        db_session.commit()

        # Convert UUIDs to string for SQLite compatibility
        change = PriceService.get_price_change(
            db_session,
            commodity_id=str(sample_commodity.id),
            market_id=str(sample_market.id),
            current_date=date(2025, 1, 15),
        )

        assert change == 0
