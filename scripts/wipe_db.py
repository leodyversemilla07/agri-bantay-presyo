import os
import sys

# Add parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry
from app.models.supply_index import SupplyIndex


def wipe_data():
    db = SessionLocal()
    try:
        print("Wiping all entries for a clean start...")
        # Order matters for foreign keys
        db.query(PriceEntry).delete()
        db.query(SupplyIndex).delete()
        db.query(Market).delete()
        db.query(Commodity).delete()
        db.commit()
        print("Successfully wiped database.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    wipe_data()
