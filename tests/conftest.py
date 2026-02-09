"""
Pytest configuration and fixtures for Agri Bantay Presyo tests.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base_class import Base
from app.db.session import get_db
from app.main import app

# Use PostgreSQL for testing - use test database or same as app
SQLALCHEMY_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", settings.sync_database_url)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Import all models to register them with Base
    from app.db import base  # noqa

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_commodity(db_session):
    """Create a sample commodity for testing."""
    import uuid

    from app.models.commodity import Commodity

    commodity = Commodity(id=uuid.uuid4(), name="Test Rice", category="Rice", variant="Local", unit="kg")
    db_session.add(commodity)
    db_session.commit()
    db_session.refresh(commodity)
    return commodity


@pytest.fixture
def sample_market(db_session):
    """Create a sample market for testing."""
    import uuid

    from app.models.market import Market

    market = Market(id=uuid.uuid4(), name="Test Market", region="NCR", city="Manila", is_regional_average=False)
    db_session.add(market)
    db_session.commit()
    db_session.refresh(market)
    return market


@pytest.fixture
def sample_price_entry(db_session, sample_commodity, sample_market):
    """Create a sample price entry for testing."""
    import uuid
    from datetime import date
    from decimal import Decimal

    from app.models.price_entry import PriceEntry

    entry = PriceEntry(
        id=uuid.uuid4(),
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
    db_session.refresh(entry)
    return entry
