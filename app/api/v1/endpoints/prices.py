from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, get_pagination_params
from app.db.session import get_db
from app.schemas.price_entry import PriceEntry
from app.services.price_service import PriceService

router = APIRouter()


@router.get("/daily", response_model=List[PriceEntry])
def get_daily_prices(
    report_date: Optional[date] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    if not report_date:
        prices = PriceService.get_latest_prices(db, skip=pagination.skip, limit=pagination.limit)
    else:
        prices = PriceService.get_prices_by_date(db, report_date=report_date)
    return prices


@router.get("/export")
def export_prices_csv(report_date: Optional[date] = None, db: Session = Depends(get_db)):
    """Export price data as CSV."""
    if report_date:
        prices = PriceService.get_prices_by_date(db, report_date=report_date)
    else:
        prices = PriceService.get_latest_prices(db, limit=1000)

    csv_lines = ["Commodity,Category,Market,Region,Low,High,Prevailing,Date"]

    for p in prices:
        commodity = p.commodity.name if p.commodity else "Unknown"
        category = p.commodity.category if p.commodity else "Unknown"
        market = p.market.name if p.market else "Unknown"
        region = p.market.region if p.market else ""
        low = p.price_low or ""
        high = p.price_high or ""
        prevailing = p.price_prevailing or p.price_average or ""
        date_str = p.report_date.isoformat() if p.report_date else ""

        csv_lines.append(f'"{commodity}","{category}","{market}","{region}",{low},{high},{prevailing},"{date_str}"')

    csv_content = "\n".join(csv_lines)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=prices_{report_date or 'latest'}.csv"},
    )
