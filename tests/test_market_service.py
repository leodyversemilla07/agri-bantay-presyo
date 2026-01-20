"""
Unit tests for MarketService.
"""

from app.models.market import Market
from app.schemas.market import MarketCreate
from app.services.market_service import MarketService


class TestMarketService:
    """Tests for MarketService methods."""

    def test_create_market(self, db_session):
        """Test creating a new market."""
        market_in = MarketCreate(name="Divisoria Market", region="NCR", city="Manila")
        result = MarketService.create(db_session, obj_in=market_in)

        assert result.name == "Divisoria Market"
        assert result.region == "NCR"
        assert result.city == "Manila"
        assert result.id is not None

    def test_get_market_by_id(self, db_session, sample_market):
        """Test retrieving a market by ID."""
        # Convert UUID to string for SQLite compatibility
        result = MarketService.get(db_session, market_id=str(sample_market.id))

        assert result is not None
        assert str(result.id) == str(sample_market.id)
        assert result.name == sample_market.name

    def test_get_market_by_name(self, db_session, sample_market):
        """Test retrieving a market by name."""
        result = MarketService.get_by_name(db_session, name=sample_market.name)

        assert result is not None
        assert result.name == sample_market.name

    def test_get_market_not_found(self, db_session):
        """Test retrieving a non-existent market returns None."""
        result = MarketService.get(db_session, market_id="00000000-0000-0000-0000-000000000000")
        assert result is None

    def test_get_multi_markets(self, db_session):
        """Test retrieving multiple markets."""
        for name in ["Market A", "Market B", "Market C"]:
            db_session.add(Market(name=name, region="NCR"))
        db_session.commit()

        results = MarketService.get_multi(db_session, skip=0, limit=10)
        assert len(results) == 3

    def test_get_multi_with_pagination(self, db_session):
        """Test pagination for markets."""
        for i in range(5):
            db_session.add(Market(name=f"Market {i}", region="NCR"))
        db_session.commit()

        page1 = MarketService.get_multi(db_session, skip=0, limit=2)
        page2 = MarketService.get_multi(db_session, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id

    def test_get_or_create_existing(self, db_session, sample_market):
        """Test get_or_create returns existing market."""
        result = MarketService.get_or_create(db_session, name=sample_market.name)

        assert result.id == sample_market.id
        count = db_session.query(Market).filter(Market.name == sample_market.name).count()
        assert count == 1

    def test_get_or_create_new(self, db_session):
        """Test get_or_create creates new market if not exists."""
        result = MarketService.get_or_create(db_session, name="New Market", region="Region V", city="Legazpi")

        assert result.name == "New Market"
        assert result.region == "Region V"

    def test_search_markets(self, db_session):
        """Test searching markets by name."""
        db_session.add(Market(name="Commonwealth Market", region="NCR"))
        db_session.add(Market(name="Kamuning Market", region="NCR"))
        db_session.add(Market(name="Divisoria", region="NCR"))
        db_session.commit()

        results = MarketService.search(db_session, query="market")
        assert len(results) == 2

    def test_search_case_insensitive(self, db_session):
        """Test search is case insensitive."""
        db_session.add(Market(name="DIVISORIA MARKET", region="NCR"))
        db_session.commit()

        results = MarketService.search(db_session, query="divisoria")
        assert len(results) == 1
