from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    from app.models.commodity import Commodity
    from app.models.market import Market
    from app.models.price_entry import PriceEntry

    total_commodities = db.query(Commodity).count()
    total_markets = db.query(Market).count()
    current_prices = db.query(PriceEntry).count()  # Or filter by latest date if needed

    return {
        "commodities": {"count": total_commodities, "change": 0},
        "markets": {"count": total_markets, "change": 0},
        "prices": {"count": current_prices, "change": 0},
    }
