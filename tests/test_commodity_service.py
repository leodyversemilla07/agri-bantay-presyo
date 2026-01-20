"""
Unit tests for CommodityService.
"""

from app.models.commodity import Commodity
from app.schemas.commodity import CommodityCreate
from app.services.commodity_service import CommodityService


class TestCommodityService:
    """Tests for CommodityService methods."""

    def test_create_commodity(self, db_session):
        """Test creating a new commodity."""
        commodity_in = CommodityCreate(name="Bangus", category="Fish", variant="Fresh", unit="kg")
        result = CommodityService.create(db_session, obj_in=commodity_in)

        assert result.name == "Bangus"
        assert result.category == "Fish"
        assert result.variant == "Fresh"
        assert result.unit == "kg"
        assert result.id is not None

    def test_get_commodity_by_id(self, db_session, sample_commodity):
        """Test retrieving a commodity by ID."""
        # Convert UUID to string for SQLite compatibility
        result = CommodityService.get(db_session, commodity_id=str(sample_commodity.id))

        assert result is not None
        assert str(result.id) == str(sample_commodity.id)
        assert result.name == sample_commodity.name

    def test_get_commodity_by_name(self, db_session, sample_commodity):
        """Test retrieving a commodity by name."""
        result = CommodityService.get_by_name(db_session, name=sample_commodity.name)

        assert result is not None
        assert result.name == sample_commodity.name

    def test_get_commodity_not_found(self, db_session):
        """Test retrieving a non-existent commodity returns None."""
        result = CommodityService.get(db_session, commodity_id="00000000-0000-0000-0000-000000000000")
        assert result is None

    def test_get_multi_commodities(self, db_session):
        """Test retrieving multiple commodities."""
        # Create multiple commodities
        for name in ["Rice A", "Rice B", "Rice C"]:
            commodity = Commodity(name=name, category="Rice", unit="kg")
            db_session.add(commodity)
        db_session.commit()

        results = CommodityService.get_multi(db_session, skip=0, limit=10)
        assert len(results) == 3

    def test_get_multi_with_category_filter(self, db_session):
        """Test filtering commodities by category."""
        # Create commodities in different categories
        db_session.add(Commodity(name="Bangus", category="Fish", unit="kg"))
        db_session.add(Commodity(name="Tilapia", category="Fish", unit="kg"))
        db_session.add(Commodity(name="Pork Liempo", category="Meat", unit="kg"))
        db_session.commit()

        results = CommodityService.get_multi(db_session, category="Fish")
        assert len(results) == 2
        assert all(c.category == "Fish" for c in results)

    def test_get_or_create_existing(self, db_session, sample_commodity):
        """Test get_or_create returns existing commodity."""
        result = CommodityService.get_or_create(db_session, name=sample_commodity.name)

        assert result.id == sample_commodity.id
        # Verify no duplicate was created
        count = db_session.query(Commodity).filter(Commodity.name == sample_commodity.name).count()
        assert count == 1

    def test_get_or_create_new(self, db_session):
        """Test get_or_create creates new commodity if not exists."""
        result = CommodityService.get_or_create(db_session, name="New Commodity", category="Vegetables", unit="kg")

        assert result.name == "New Commodity"
        assert result.category == "Vegetables"

    def test_search_commodities(self, db_session):
        """Test searching commodities by name."""
        db_session.add(Commodity(name="Red Onion", category="Vegetables"))
        db_session.add(Commodity(name="White Onion", category="Vegetables"))
        db_session.add(Commodity(name="Garlic", category="Spices"))
        db_session.commit()

        results = CommodityService.search(db_session, query="onion")
        assert len(results) == 2
        assert all("Onion" in c.name for c in results)

    def test_search_case_insensitive(self, db_session):
        """Test search is case insensitive."""
        db_session.add(Commodity(name="BANGUS", category="Fish"))
        db_session.commit()

        results = CommodityService.search(db_session, query="bangus")
        assert len(results) == 1
        assert results[0].name == "BANGUS"
