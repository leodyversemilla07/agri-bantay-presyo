"""
Pytest configuration and fixtures for Agri Bantay Presyo tests.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base_class import Base
from app.db.session import get_db
from app.main import app

TEST_API_KEY = "test-api-key"
TEST_ADMIN_API_KEY = "test-admin-api-key"

# Default to in-memory SQLite for tests so the suite does not depend on a local
# PostgreSQL instance. TEST_DATABASE_URL can still override this when needed.
SQLALCHEMY_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite://")

engine_kwargs = {"pool_pre_ping": True}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def configure_test_api_key():
    """Ensure protected write endpoints require a deterministic test API key."""
    original_api_key = settings.API_KEY
    original_service_api_keys = dict(settings.SERVICE_API_KEYS)
    original_admin_api_keys = dict(settings.ADMIN_API_KEYS)
    settings.API_KEY = None
    settings.SERVICE_API_KEYS = {"test-service": TEST_API_KEY}
    settings.ADMIN_API_KEYS = {"test-admin": TEST_ADMIN_API_KEY}
    try:
        yield
    finally:
        settings.API_KEY = original_api_key
        settings.SERVICE_API_KEYS = original_service_api_keys
        settings.ADMIN_API_KEYS = original_admin_api_keys


@pytest.fixture
def auth_headers():
    """Headers for authenticated write requests."""
    return {settings.API_KEY_HEADER: TEST_API_KEY}


@pytest.fixture
def admin_auth_headers():
    """Headers for admin-only endpoints."""
    return {settings.API_KEY_HEADER: TEST_ADMIN_API_KEY}


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
