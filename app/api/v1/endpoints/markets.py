from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, get_pagination_params, verify_api_key
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.market import Market, MarketCreate
from app.schemas.pagination import PaginatedResponse
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[Market])
@limiter.limit("200/minute")
def read_markets(
    request: Request,
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    q: str | None = Query(None, description="Case-insensitive market name search"),
):
    items = MarketService.get_multi(db, skip=pagination.skip, limit=pagination.limit, query=q)
    total = MarketService.count_multi(db, query=q)
    return {"items": items, "total": total, "skip": pagination.skip, "limit": pagination.limit}


@router.post("/", response_model=Market, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_market(
    request: Request,
    response: Response,
    market_in: MarketCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    existing = MarketService.get_by_name(db, name=market_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Market already exists")
    market = MarketService.create(db, obj_in=market_in)
    response.headers["Location"] = f"{settings.API_V1_STR}/markets/{market.id}"
    return market


@router.get("/{market_id}", response_model=Market)
@limiter.limit("200/minute")
def read_market(request: Request, market_id: str, db: Session = Depends(get_db)):
    market = MarketService.get(db, market_id=market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/search/{query}", response_model=List[Market], include_in_schema=False)
@limiter.limit("100/minute")
def search_markets(request: Request, query: str, db: Session = Depends(get_db)):
    """Legacy alias for market search."""
    return MarketService.get_multi(db, limit=20, query=query)
