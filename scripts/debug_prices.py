from app.db.session import SessionLocal
from app.services.price_service import PriceService
from app.models.price_entry import PriceEntry
import logging
import sys

# Register models
from app.db import base
from sqlalchemy.orm import configure_mappers
try:
    configure_mappers()
except Exception as e:
    print(f"Configure mappers failed: {e}")

logging.basicConfig(level=logging.INFO)

def test_prices_logic():
    print("Testing PriceService logic...")
    db = SessionLocal()
    try:
        # Test get_latest_prices
        prices = PriceService.get_latest_prices(db, limit=5)
        print(f"Found {len(prices)} prices")
        for p in prices:
            print(f"- {p.commodity.name} at {p.market.name}: {p.price_prevailing}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_prices_logic()
