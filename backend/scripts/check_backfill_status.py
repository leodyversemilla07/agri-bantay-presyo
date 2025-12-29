from app.db.session import SessionLocal
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry
from app.models.supply_index import SupplyIndex
from sqlalchemy import func

def check_count():
    db = SessionLocal()
    try:
        count = db.query(func.count(PriceEntry.id)).scalar()
        print(f"Total Price Entries: {count}")
        
        # Check distinct dates
        dates = db.query(PriceEntry.report_date).distinct().order_by(PriceEntry.report_date).all()
        print(f"Distinct Dates: {len(dates)}")
        if dates:
            print(f"Range: {dates[0][0]} to {dates[-1][0]}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_count()
