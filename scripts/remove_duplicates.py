from app.db.session import SessionLocal
from app.db import base
from app.models.price_entry import PriceEntry
from collections import defaultdict

def remove_duplicates():
    db = SessionLocal()
    try:
        print("Fetching all entries to identify duplicates...")
        entries = db.query(PriceEntry).all()
        
        seen = {} # (commodity_id, market_id, report_date, report_type) -> id
        to_delete = []
        
        for entry in entries:
            key = (entry.commodity_id, entry.market_id, entry.report_date, entry.report_type)
            if key in seen:
                to_delete.append(entry.id)
            else:
                seen[key] = entry.id
        
        if to_delete:
            print(f"Found {len(to_delete)} duplicate entries. Deleting...")
            # Delete in chunks to be safe
            for i in range(0, len(to_delete), 100):
                chunk = to_delete[i:i+100]
                db.query(PriceEntry).filter(PriceEntry.id.in_(chunk)).delete(synchronize_session=False)
            db.commit()
            print("Successfully removed duplicates.")
        else:
            print("No duplicates found.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_duplicates()
