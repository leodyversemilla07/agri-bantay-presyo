"""
Unit tests for PriceService.
"""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry
from app.services.price_service import PriceService


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

    def test_get_latest_prices_returns_latest_snapshot_only(self, db_session, sample_price_entry):
        """Test latest prices only returns entries from the latest report date."""
        latest_entry = PriceEntry(
            commodity_id=sample_price_entry.commodity_id,
            market_id=sample_price_entry.market_id,
            report_date=date(2025, 1, 20),
            price_prevailing=Decimal("60.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(latest_entry)
        db_session.commit()

        results = PriceService.get_latest_prices(db_session, skip=0, limit=10)

        assert len(results) == 1
        assert results[0].report_date == date(2025, 1, 20)

    def test_count_prices_defaults_to_latest_snapshot(self, db_session, sample_price_entry):
        """Test counting prices without a date only counts the latest snapshot."""
        latest_entry = PriceEntry(
            commodity_id=sample_price_entry.commodity_id,
            market_id=sample_price_entry.market_id,
            report_date=date(2025, 1, 20),
            price_prevailing=Decimal("60.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(latest_entry)
        db_session.commit()

        assert PriceService.count_prices(db_session) == 1

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

    def test_get_dashboard_snapshot_stats_uses_previous_available_snapshot(self, db_session, sample_commodity, sample_market):
        """Test dashboard deltas compare against the previous available snapshot."""
        extra_commodity = Commodity(id=uuid4(), name="Test Onion", category="Vegetable", unit="kg")
        extra_market = Market(id=uuid4(), name="North Market", region="NCR", city="Quezon City")
        db_session.add_all([extra_commodity, extra_market])

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "110.00")
        _add_price(db_session, extra_commodity.id, extra_market.id, date(2025, 1, 20), "80.00")
        db_session.commit()

        stats = PriceService.get_dashboard_snapshot_stats(db_session)

        assert stats["latest_report_date"] == date(2025, 1, 20)
        assert stats["previous_report_date"] == date(2025, 1, 15)
        assert stats["commodities"]["count"] == 2
        assert stats["commodities"]["change"] == 1
        assert stats["markets"]["count"] == 2
        assert stats["markets"]["change"] == 1
        assert stats["prices"]["count"] == 2
        assert stats["prices"]["change"] == 1

    def test_get_commodity_trend_summary_aggregates_across_markets(self, db_session, sample_commodity, sample_market):
        """Test commodity summary averages prevailing prices across markets when market_id is omitted."""
        second_market = Market(id=uuid4(), name="South Market", region="NCR", city="Makati")
        db_session.add(second_market)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        summary = PriceService.get_commodity_trend_summary(db_session, commodity_id=sample_commodity.id)

        assert summary["latest_report_date"] == date(2025, 1, 20)
        assert summary["previous_report_date"] == date(2025, 1, 15)
        assert summary["current_prevailing_price"] == Decimal("140.00")
        assert summary["previous_prevailing_price"] == Decimal("110.00")
        assert summary["absolute_change"] == Decimal("30.00")
        assert summary["percent_change"] == 27.3
        assert summary["market_count"] == 2

    def test_get_commodity_trend_summary_for_specific_market(self, db_session, sample_commodity, sample_market):
        """Test market-specific commodity summary does not aggregate across markets."""
        second_market = Market(id=uuid4(), name="South Market", region="NCR", city="Makati")
        db_session.add(second_market)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        summary = PriceService.get_commodity_trend_summary(
            db_session,
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
        )

        assert summary["current_prevailing_price"] == Decimal("130.00")
        assert summary["previous_prevailing_price"] == Decimal("100.00")
        assert summary["absolute_change"] == Decimal("30.00")
        assert summary["percent_change"] == 30.0
        assert summary["market_count"] == 1

    def test_get_commodity_trend_summary_without_previous_snapshot_returns_null_changes(
        self, db_session, sample_commodity, sample_market
    ):
        """Test summary returns null change fields when there is no earlier snapshot."""
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        db_session.commit()

        summary = PriceService.get_commodity_trend_summary(db_session, commodity_id=sample_commodity.id)

        assert summary["previous_report_date"] is None
        assert summary["previous_prevailing_price"] is None
        assert summary["absolute_change"] is None
        assert summary["percent_change"] is None

    def test_get_commodity_trend_series_returns_chronological_points(self, db_session, sample_commodity, sample_market):
        """Test trend series is returned in chronological order."""
        second_market = Market(id=uuid4(), name="South Market", region="NCR", city="Makati")
        db_session.add(second_market)

        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 15), "100.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 15), "120.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 18), "110.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 18), "130.00")
        _add_price(db_session, sample_commodity.id, sample_market.id, date(2025, 1, 20), "130.00")
        _add_price(db_session, sample_commodity.id, second_market.id, date(2025, 1, 20), "150.00")
        db_session.commit()

        points = PriceService.get_commodity_trend_series(db_session, commodity_id=sample_commodity.id, limit=2)

        assert len(points) == 2
        assert points[0]["report_date"] == date(2025, 1, 18)
        assert points[1]["report_date"] == date(2025, 1, 20)
        assert points[0]["prevailing_price"] == Decimal("120.00")
        assert points[1]["prevailing_price"] == Decimal("140.00")
        assert points[1]["market_count"] == 2

    def test_db_enforces_unique_price_entry_identity(self, db_session, sample_commodity, sample_market):
        """Test the database rejects duplicate price entries for the same identity tuple."""
        entry1 = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 20),
            price_prevailing=Decimal("50.00"),
            report_type="DAILY_RETAIL",
        )
        entry2 = PriceEntry(
            commodity_id=sample_commodity.id,
            market_id=sample_market.id,
            report_date=date(2025, 1, 20),
            price_prevailing=Decimal("55.00"),
            report_type="DAILY_RETAIL",
        )
        db_session.add(entry1)
        db_session.commit()

        db_session.add(entry2)
        try:
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
        else:
            raise AssertionError("Expected unique constraint to reject duplicate price entry identity")
