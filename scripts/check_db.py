import os
import sys

# Add parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models import Commodity, Market, PriceEntry

db = SessionLocal()
try:
    commodities = db.query(Commodity).count()
    markets = db.query(Market).count()
    prices = db.query(PriceEntry).count()
    print(f"Commodities: {commodities}")
    print(f"Markets: {markets}")
    print(f"Prices: {prices}")
finally:
    db.close()
