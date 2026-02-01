from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, get_pagination_params, verify_api_key
from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.market import Market, MarketCreate
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/", response_model=List[Market])
@limiter.limit("200/minute")
def read_markets(
    request: Request,
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
):
    from app.models.market import Market as MarketModel

    markets = db.query(MarketModel).offset(pagination.skip).limit(pagination.limit).all()
    return markets


@router.post("/", response_model=Market)
@limiter.limit("30/minute")
def create_market(
    request: Request,
    market_in: MarketCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    existing = MarketService.get_by_name(db, name=market_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Market already exists")
    return MarketService.create(db, obj_in=market_in)


@router.get("/{market_id}", response_model=Market)
@limiter.limit("200/minute")
def read_market(request: Request, market_id: str, db: Session = Depends(get_db)):
    market = MarketService.get(db, market_id=market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/search/{query}", response_model=List[Market])
@limiter.limit("100/minute")
def search_markets(request: Request, query: str, db: Session = Depends(get_db)):
    """Search markets by name."""
    return MarketService.search(db, query=query, limit=20)
