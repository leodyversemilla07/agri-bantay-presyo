from app.db import base
from app.db.session import SessionLocal
from app.services.market_service import MarketService
from app.models.market import Market
import logging

logging.basicConfig(level=logging.INFO)

def test_markets_logic():
    print("Testing MarketService logic...")
    db = SessionLocal()
    try:
        markets = MarketService.get_multi(db)
        print(f"Found {len(markets)} markets")
        for m in markets:
            print(f"- {m.name}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_markets_logic()
