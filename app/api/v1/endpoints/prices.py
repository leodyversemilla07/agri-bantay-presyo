from typing import List

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, get_pagination_params, get_price_filters
from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.price_filters import PriceFilters, PriceView
from app.schemas.price_entry import PaginatedPriceResponse, PriceEntry, PriceEntryCompact, PriceEntryListItem
from app.services.price_service import PriceService

router = APIRouter()


def _fetch_prices(
    db: Session,
    filters: PriceFilters,
    pagination: PaginationParams,
) -> List[PriceEntry]:
    return PriceService.get_filtered_prices(
        db,
        filters=filters,
        skip=pagination.skip,
        limit=pagination.limit,
    )


def _shape_prices(prices: List[PriceEntry], view: PriceView) -> List[PriceEntryListItem]:
    if view == PriceView.COMPACT:
        return PriceService.to_compact_prices(prices)
    return prices


def _export_filename(filters: PriceFilters) -> str:
    if filters.report_date is not None:
        return f"prices_{filters.report_date.isoformat()}.csv"
    if filters.uses_date_range:
        start = filters.start_date.isoformat() if filters.start_date is not None else "open"
        end = filters.end_date.isoformat() if filters.end_date is not None else "open"
        return f"prices_{start}_to_{end}.csv"
    return "prices_latest.csv"


@router.get("/", response_model=PaginatedPriceResponse)
@limiter.limit("200/minute")
def get_prices(
    request: Request,
    filters: PriceFilters = Depends(get_price_filters),
    view: PriceView = PriceView.FULL,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    prices = _fetch_prices(db, filters=filters, pagination=pagination)
    total = PriceService.count_filtered_prices(db, filters=filters)
    return {"items": _shape_prices(prices, view), "total": total, "skip": pagination.skip, "limit": pagination.limit}


@router.get("/daily", response_model=List[PriceEntry | PriceEntryCompact], include_in_schema=False)
@limiter.limit("200/minute")
def get_daily_prices_legacy(
    request: Request,
    filters: PriceFilters = Depends(get_price_filters),
    view: PriceView = PriceView.FULL,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    return _shape_prices(_fetch_prices(db, filters=filters, pagination=pagination), view)


@router.get("/export")
@limiter.limit("20/minute")
def export_prices_csv(
    request: Request,
    filters: PriceFilters = Depends(get_price_filters),
    db: Session = Depends(get_db),
):
    """Export price data as CSV."""
    prices = PriceService.get_filtered_prices(db, filters=filters, limit=None)

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
        headers={"Content-Disposition": f"attachment; filename={_export_filename(filters)}"},
    )
