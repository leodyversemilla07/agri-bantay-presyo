from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.services.price_service import PriceService
from app.schemas.price_entry import PriceEntry

router = APIRouter()

from app.api.deps import get_pagination_params, PaginationParams

@router.get("/daily", response_model=List[PriceEntry])
def get_daily_prices(
    report_date: Optional[date] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    if not report_date:
        prices = PriceService.get_latest_prices(db, skip=pagination.skip, limit=pagination.limit)
    else:
        # Note: Pagination for date-filtered results wasn't requested but is good practice.
        # For now, we only applied it to get_latest_prices in the service.
        prices = PriceService.get_prices_by_date(db, report_date=report_date)
    return prices

@router.get("/weekly")
def get_weekly_prices(db: Session = Depends(get_db)):
    # Placeholder for weekly logic
    return []
