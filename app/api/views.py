import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.cache import get_cached_data
from app.db.session import get_db
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry
from app.services.price_service import PriceService

router = APIRouter()

# Get absolute path to templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_ticker_items(db: Session) -> List[dict]:
    """Get latest prices for ticker display."""
    commodities = db.query(Commodity).limit(10).all()
    if not commodities:
        return [{"name": "No Data", "price": 0, "change": 0}]

    comm_ids = [c.id for c in commodities]

    # Fetch latest prices for these commodities efficiently
    subq = (
        db.query(
            PriceEntry.id,
            func.row_number()
            .over(partition_by=PriceEntry.commodity_id, order_by=desc(PriceEntry.report_date))
            .label("rn"),
        )
        .filter(PriceEntry.commodity_id.in_(comm_ids))
        .subquery()
    )

    latest_entries = (
        db.query(PriceEntry)
        .join(subq, PriceEntry.id == subq.c.id)
        .filter(subq.c.rn == 1)
        .all()
    )

    latest_map = {str(e.commodity_id): e for e in latest_entries}

    # Identify (commodity, market) pairs to fetch history for
    pairs = [(e.commodity_id, e.market_id) for e in latest_entries]

    history_map = {}
    if pairs:
        # Construct filter for these pairs
        filters = [
            and_(PriceEntry.commodity_id == c_id, PriceEntry.market_id == m_id)
            for c_id, m_id in pairs
        ]

        # Fetch top 2 entries for each pair (latest + previous)
        subq_prev = (
            db.query(
                PriceEntry.id,
                PriceEntry.commodity_id,
                PriceEntry.market_id,
                func.row_number()
                .over(
                    partition_by=(PriceEntry.commodity_id, PriceEntry.market_id),
                    order_by=desc(PriceEntry.report_date),
                )
                .label("rn"),
            )
            .filter(or_(*filters))
            .subquery()
        )

        history_entries = (
            db.query(PriceEntry)
            .join(subq_prev, PriceEntry.id == subq_prev.c.id)
            .filter(subq_prev.c.rn <= 2)
            .all()
        )

        for entry in history_entries:
            key = (str(entry.commodity_id), str(entry.market_id))
            if key not in history_map:
                history_map[key] = []
            history_map[key].append(entry)

        # Ensure sorted
        for key in history_map:
            history_map[key].sort(key=lambda x: x.report_date, reverse=True)

    ticker_items = []
    for comm in commodities:
        latest = latest_map.get(str(comm.id))

        if latest:
            price = latest.price_prevailing or latest.price_average or 0

            # Calculate change
            key = (str(comm.id), str(latest.market_id))
            history = history_map.get(key, [])

            change = 0
            # Find the first entry strictly before the latest report date
            prev_entry = None
            for h in history:
                if h.report_date < latest.report_date:
                    prev_entry = h
                    break

            if prev_entry:
                prev_price = prev_entry.price_prevailing or 0
                if prev_price > 0:
                    current_price = price
                    change = round(((current_price - prev_price) / prev_price) * 100, 1)

            ticker_items.append({
                "name": comm.name[:20],
                "price": float(price) if price else 0.0,
                "change": float(change) if change else 0.0,
            })

    return ticker_items if ticker_items else [{"name": "No Data", "price": 0.0, "change": 0.0}]


def get_dashboard_stats(db: Session) -> dict:
    """Get dashboard statistics."""
    return {
        "commodities": {"count": db.query(Commodity).count(), "change": 0},
        "markets": {"count": db.query(Market).count(), "change": 0},
        "prices": {"count": db.query(PriceEntry).count(), "change": 0},
    }


def get_chart_data(db: Session, commodity_id: str, limit: int = 30) -> List[dict]:
    """Get chart data for a commodity."""
    history = PriceService.get_commodity_history(db, commodity_id=commodity_id, limit=limit)

    chart_data = []
    for h in reversed(history):
        from datetime import datetime

        date_obj = h.report_date if hasattr(h, "report_date") else h.get("report_date")
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj)

        price = h.price_prevailing if hasattr(h, "price_prevailing") else h.get("price_prevailing", 0)
        price = price or (h.price_average if hasattr(h, "price_average") else h.get("price_average", 0)) or 0
        low = h.price_low if hasattr(h, "price_low") else h.get("price_low", 0)
        high = h.price_high if hasattr(h, "price_high") else h.get("price_high", 0)

        chart_data.append(
            {
                "date": date_obj.strftime("%b %d") if date_obj else "",
                "price": float(price) if price else 0,
                "low": float(low) if low else 0,
                "high": float(high) if high else 0,
            }
        )

    return chart_data


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with overview dashboard."""
    ticker_items = await get_cached_data("dashboard:ticker_items", lambda: get_ticker_items(db), ttl=300)
    stats = await get_cached_data("dashboard:stats", lambda: get_dashboard_stats(db), ttl=300)

    # Get default commodity for chart
    default_commodity = db.query(Commodity).first()
    default_commodity_name = default_commodity.name if default_commodity else "No Data"

    chart_data = []
    if default_commodity:
        chart_data = get_chart_data(db, default_commodity.id, limit=30)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "ticker_items": ticker_items,
            "stats": stats,
            "default_commodity": default_commodity_name,
            "chart_data": chart_data,
            "chart_data_json": json.dumps(chart_data),
        },
    )


@router.get("/markets", response_class=HTMLResponse)
async def markets_page(request: Request, db: Session = Depends(get_db), q: str = None):
    """Markets page with filterable data table."""
    ticker_items = get_ticker_items(db)

    # Get all markets
    markets = db.query(Market).all()

    # Get categories
    categories = db.query(Commodity.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    # Get unique regions
    regions = db.query(Market.region).distinct().all()
    regions = [r[0] for r in regions if r[0]]

    # Get latest prices with commodity and market info (using joinedload to avoid N+1)
    prices_query = (
        db.query(PriceEntry)
        .options(joinedload(PriceEntry.commodity), joinedload(PriceEntry.market))
        .order_by(desc(PriceEntry.report_date))
        .limit(500)
        .all()
    )

    prices_data = []
    for p in prices_query:
        commodity = p.commodity
        market = p.market

        prices_data.append(
            {
                "id": str(p.id),
                "commodity_id": str(p.commodity_id) if p.commodity_id else "",
                "commodity_name": commodity.name if commodity else "Unknown",
                "category": commodity.category if commodity else "Unknown",
                "market_id": str(p.market_id) if p.market_id else "",
                "market_name": market.name if market else "Unknown",
                "market_region": market.region if market else "",
                "price_low": float(p.price_low) if p.price_low else None,
                "price_high": float(p.price_high) if p.price_high else None,
                "price_prevailing": float(p.price_prevailing) if p.price_prevailing else None,
                "price_average": float(p.price_average) if p.price_average else None,
                "report_date": p.report_date.isoformat() if p.report_date else None,
            }
        )

    markets_data = [{"id": str(m.id), "name": m.name, "region": m.region} for m in markets]

    return templates.TemplateResponse(
        request=request,
        name="markets.html",
        context={
            "ticker_items": ticker_items,
            "markets": markets_data,
            "categories": categories,
            "regions": regions,
            "prices_json": json.dumps(prices_data),
            "search_query": q or "",
        },
    )


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, db: Session = Depends(get_db)):
    """Analytics page with advanced charts."""
    ticker_items = get_ticker_items(db)
    stats = get_dashboard_stats(db)

    # Get all commodities
    commodities = db.query(Commodity).all()
    commodities_data = [{"id": str(c.id), "name": c.name} for c in commodities]

    # Get default commodity
    default_commodity = commodities[0] if commodities else None
    default_commodity_id = str(default_commodity.id) if default_commodity else ""

    chart_data = []
    current_price = 0
    if default_commodity:
        chart_data = get_chart_data(db, default_commodity.id, limit=30)
        if chart_data:
            current_price = chart_data[-1]["price"]

    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={
            "ticker_items": ticker_items,
            "stats": stats,
            "commodities": commodities_data,
            "commodities_json": json.dumps(commodities_data),
            "default_commodity_id": default_commodity_id,
            "chart_data_json": json.dumps(chart_data),
            "current_price": current_price,
        },
    )
