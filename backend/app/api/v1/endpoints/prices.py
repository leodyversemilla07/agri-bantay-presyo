from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.services.price_service import PriceService
from app.schemas.price_entry import PriceEntry

router = APIRouter()

@router.get("/daily")
def get_daily_prices(
    report_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    if not report_date:
        prices = PriceService.get_latest_prices(db)
    else:
        prices = PriceService.get_prices_by_date(db, report_date=report_date)
    
    # Manual serialization to avoid Pydantic/SQLAlchemy lazy loading issues
    result = []
    for p in prices:
        try:
            item = {
                "id": str(p.id),
                "commodity_id": str(p.commodity_id),
                "market_id": str(p.market_id),
                "report_date": p.report_date.isoformat() if p.report_date else None,
                "price_low": float(p.price_low) if p.price_low is not None else None,
                "price_high": float(p.price_high) if p.price_high is not None else None,
                "price_prevailing": float(p.price_prevailing) if p.price_prevailing is not None else None,
                "price_average": float(p.price_average) if p.price_average is not None else None,
                "report_type": str(p.report_type),
            }
            # Safely access relationships? 
            # If joinedload was used, they should be loaded.
            # But if relationship is broken, this might fail.
            # Let's check attributes without accessing them first?
            # No, standard access.
            if hasattr(p, 'commodity') and p.commodity:
                item["commodity"] = {"name": p.commodity.name, "category": p.commodity.category}
            else:
                item["commodity"] = None
                
            if hasattr(p, 'market') and p.market:
                item["market"] = {"name": p.market.name, "region": p.market.region}
            else:
                item["market"] = None
                
            result.append(item)
        except Exception as e:
            print(f"Error serializing price entry {p.id}: {e}")
            continue
    return result

@router.get("/weekly")
def get_weekly_prices(db: Session = Depends(get_db)):
    # Placeholder for weekly logic
    return []
