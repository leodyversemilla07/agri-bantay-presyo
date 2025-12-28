from app.db.session import SessionLocal
from app.db import base
from app.models.price_entry import PriceEntry
from app.models.commodity import Commodity
from sqlalchemy import delete

def wipe_data():
    db = SessionLocal()
    try:
        print("Wiping all price entries and commodities for a clean start...")
        db.query(PriceEntry).delete()
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
