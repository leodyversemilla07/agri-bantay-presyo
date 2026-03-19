from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.analytics import CommodityTrendSeries, CommodityTrendSummary, MarketTrendSeries, MarketTrendSummary
from app.schemas.price_entry import PriceEntry
from app.services.price_service import PriceService

router = APIRouter()


@router.get("/commodities/{commodity_id}/summary", response_model=CommodityTrendSummary)
@limiter.limit("100/minute")
def get_commodity_trend_summary(
    request: Request,
    commodity_id: UUID,
    market_id: UUID | None = None,
    report_date: date | None = None,
    db: Session = Depends(get_db),
):
    summary = PriceService.get_commodity_trend_summary(
        db,
        commodity_id=commodity_id,
        market_id=market_id,
        report_date=report_date,
    )
    if summary is None:
        raise HTTPException(status_code=404, detail="Commodity trend data not found")
    return summary


@router.get("/commodities/{commodity_id}/series", response_model=CommodityTrendSeries)
@limiter.limit("100/minute")
def get_commodity_trend_series(
    request: Request,
    commodity_id: UUID,
    market_id: UUID | None = None,
    limit: int = 30,
    db: Session = Depends(get_db),
):
    points = PriceService.get_commodity_trend_series(
        db,
        commodity_id=commodity_id,
        market_id=market_id,
        limit=limit,
    )
    return {"commodity_id": commodity_id, "market_id": market_id, "points": points}


@router.get("/markets/{market_id}/summary", response_model=MarketTrendSummary)
@limiter.limit("100/minute")
def get_market_trend_summary(
    request: Request,
    market_id: UUID,
    commodity_id: UUID | None = None,
    report_date: date | None = None,
    db: Session = Depends(get_db),
):
    summary = PriceService.get_market_trend_summary(
        db,
        market_id=market_id,
        commodity_id=commodity_id,
        report_date=report_date,
    )
    if summary is None:
        raise HTTPException(status_code=404, detail="Market trend data not found")
    return summary


@router.get("/markets/{market_id}/series", response_model=MarketTrendSeries)
@limiter.limit("100/minute")
def get_market_trend_series(
    request: Request,
    market_id: UUID,
    commodity_id: UUID | None = None,
    limit: int = 30,
    db: Session = Depends(get_db),
):
    points = PriceService.get_market_trend_series(
        db,
        market_id=market_id,
        commodity_id=commodity_id,
        limit=limit,
    )
    return {"market_id": market_id, "commodity_id": commodity_id, "points": points}


@router.get("/history/{commodity_id}", response_model=List[PriceEntry], include_in_schema=False)
@limiter.limit("100/minute")
def get_commodity_history(
    request: Request, commodity_id: UUID, limit: int = 30, db: Session = Depends(get_db)
):
    return PriceService.get_commodity_history(db, commodity_id=commodity_id, limit=limit)
