from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.analytics import DashboardStats
from app.services.price_service import PriceService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
@limiter.limit("200/minute")
def get_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    return PriceService.get_dashboard_snapshot_stats(db)
