import json
import time
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry
from app.services.price_service import PriceService

router = APIRouter()

# Get absolute path to templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Cache for ticker items
_TICKER_CACHE = {
    "data": [],
    "last_updated": 0,
    "ttl": 300,  # 5 minutes
}


def get_ticker_items(db: Session) -> List[dict]:
    """Get latest prices for ticker display."""
    # Check cache
    now = time.time()
    if _TICKER_CACHE["data"] and (now - _TICKER_CACHE["last_updated"] < _TICKER_CACHE["ttl"]):
        # Return a copy to prevent mutation of cached data
        return list(_TICKER_CACHE["data"])

    commodities = db.query(Commodity).limit(10).all()
    ticker_items = []

    for comm in commodities:
        latest_price = (
            db.query(PriceEntry)
            .filter(PriceEntry.commodity_id == comm.id)
            .order_by(desc(PriceEntry.report_date))
            .first()
        )

        if latest_price:
            price = latest_price.price_prevailing or latest_price.price_average or 0
            change = PriceService.get_price_change(db, comm.id, latest_price.market_id, latest_price.report_date)
            ticker_items.append({"name": comm.name[:20], "price": price, "change": change})

    result = ticker_items if ticker_items else [{"name": "No Data", "price": 0, "change": 0}]

    # Update cache
    _TICKER_CACHE["data"] = result
    _TICKER_CACHE["last_updated"] = now

    return result


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
    ticker_items = get_ticker_items(db)
    stats = get_dashboard_stats(db)

    # Get default commodity for chart
    default_commodity = db.query(Commodity).first()
    default_commodity_name = default_commodity.name if default_commodity else "No Data"

    chart_data = []
    if default_commodity:
        chart_data = get_chart_data(db, default_commodity.id, limit=30)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
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

    # Get latest prices with commodity and market info
    prices_query = db.query(PriceEntry).order_by(desc(PriceEntry.report_date)).limit(500).all()

    prices_data = []
    for p in prices_query:
        commodity = db.query(Commodity).filter(Commodity.id == p.commodity_id).first()
        market = db.query(Market).filter(Market.id == p.market_id).first()

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
        "markets.html",
        {
            "request": request,
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
        "analytics.html",
        {
            "request": request,
            "ticker_items": ticker_items,
            "stats": stats,
            "commodities": commodities_data,
            "commodities_json": json.dumps(commodities_data),
            "default_commodity_id": default_commodity_id,
            "chart_data_json": json.dumps(chart_data),
            "current_price": current_price,
        },
    )
