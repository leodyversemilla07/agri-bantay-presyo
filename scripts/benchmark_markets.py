import time
import uuid
import random
import os
from datetime import date
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import desc

from app.db.base_class import Base
# Import models to ensure they are registered
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry

# Use SQLite for benchmarking
DB_FILE = "benchmark_test.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_FILE}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    print("Seeding database...")
    # Create Commodities
    commodities = []
    for i in range(50):
        c = Commodity(
            id=uuid.uuid4(),
            name=f"Commodity {i}",
            category="Category A",
            variant="Variant X",
            unit="kg"
        )
        db.add(c)
        commodities.append(c)

    # Create Markets
    markets = []
    for i in range(50):
        m = Market(
            id=uuid.uuid4(),
            name=f"Market {i}",
            region="Region 1",
            city="City Z"
        )
        db.add(m)
        markets.append(m)

    db.commit()

    # Create PriceEntries
    for i in range(500):
        p = PriceEntry(
            id=uuid.uuid4(),
            commodity_id=random.choice(commodities).id,
            market_id=random.choice(markets).id,
            report_date=date(2025, 1, 1),
            price_low=10,
            price_high=20,
            price_prevailing=15,
            price_average=15
        )
        db.add(p)

    db.commit()
    db.close()
    print("Database seeded.")

def run_baseline():
    print("\nRunning Baseline (N+1)...")
    db = SessionLocal()

    # Enable query counting
    query_count = 0

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        query_count += 1

    listener = event.listen(engine, "before_cursor_execute", before_cursor_execute)

    start_time = time.time()

    # Code mimics app/api/views.py BEFORE optimization
    prices_query = db.query(PriceEntry).order_by(desc(PriceEntry.report_date)).limit(500).all()

    prices_data = []
    for p in prices_query:
        commodity = db.query(Commodity).filter(Commodity.id == p.commodity_id).first()
        market = db.query(Market).filter(Market.id == p.market_id).first()

        prices_data.append(
            {
                "id": str(p.id),
                "commodity_name": commodity.name if commodity else "Unknown",
                "market_name": market.name if market else "Unknown",
            }
        )

    end_time = time.time()

    event.remove(engine, "before_cursor_execute", before_cursor_execute)

    print(f"Baseline Result: {query_count} queries in {end_time - start_time:.4f} seconds")
    return query_count, end_time - start_time

def run_optimized():
    print("\nRunning Optimized (joinedload)...")
    db = SessionLocal()

    # Enable query counting
    query_count = 0

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        query_count += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)

    start_time = time.time()

    # Code mimics app/api/views.py AFTER optimization
    prices_query = (
        db.query(PriceEntry)
        .options(joinedload(PriceEntry.commodity), joinedload(PriceEntry.market))
        .order_by(desc(PriceEntry.report_date))
        .limit(500)
        .all()
    )

    prices_data = []
    for p in prices_query:
        # Accessing relationships directly
        commodity = p.commodity
        market = p.market

        prices_data.append(
            {
                "id": str(p.id),
                "commodity_name": commodity.name if commodity else "Unknown",
                "market_name": market.name if market else "Unknown",
            }
        )

    end_time = time.time()

    event.remove(engine, "before_cursor_execute", before_cursor_execute)

    print(f"Optimized Result: {query_count} queries in {end_time - start_time:.4f} seconds")
    return query_count, end_time - start_time

def cleanup():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    print("\nCleanup done.")

if __name__ == "__main__":
    try:
        setup_db()
        b_count, b_time = run_baseline()
        o_count, o_time = run_optimized()

        improvement = b_time / o_time if o_time > 0 else 0
        print(f"\nSpeedup: {improvement:.2f}x")
        print(f"Query Reduction: {b_count} -> {o_count}")

    finally:
        cleanup()
