import os
import sys

# Add parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db import base
from app.models.price_entry import PriceEntry
from app.models.commodity import Commodity
from app.models.market import Market

def show_stored_data():
    db = SessionLocal()
    try:
        entries = db.query(PriceEntry).join(Commodity).join(Market).order_by(PriceEntry.report_date.desc(), Commodity.name).limit(30).all()
        
        if not entries:
            print("No data found in the database.")
            return

        print("\n=== LATEST FETCHED PRICE DATA (Sample 30 rows) ===")
        print(f"{'DATE':<12} | {'COMMODITY':<30} | {'PRICE (PHP)':<12} | {'LOW-HIGH'}")
        print("-" * 75)

        for entry in entries:
            name = entry.commodity.name
            price = f"P{entry.price_prevailing:.2f}" if entry.price_prevailing else "N/A"
            low = f"{entry.price_low:.2f}" if entry.price_low else "?"
            high = f"{entry.price_high:.2f}" if entry.price_high else "?"
            
            print(f"{str(entry.report_date):<12} | {name[:30]:<30} | {price:<12} | {low}-{high}")

        total = db.query(PriceEntry).count()
        print("-" * 75)
        print(f"Dataset total: {total} entries. Use API for full access.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    show_stored_data()
