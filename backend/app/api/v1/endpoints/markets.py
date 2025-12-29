from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.market import Market, MarketCreate
from app.services.market_service import MarketService

router = APIRouter()

from app.api.deps import PaginationParams, get_pagination_params

@router.get("/", response_model=List[Market])
def read_markets(
    db: Session = Depends(get_db), 
    pagination: PaginationParams = Depends(get_pagination_params)
):
    from app.models.market import Market as MarketModel
    markets = db.query(MarketModel).offset(pagination.skip).limit(pagination.limit).all()
    return markets

@router.post("/", response_model=Market)
def create_market(market_in: MarketCreate, db: Session = Depends(get_db)):
    existing = MarketService.get_by_name(db, name=market_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Market already exists")
    return MarketService.create(db, obj_in=market_in)

@router.get("/{market_id}", response_model=Market)
def read_market(market_id: str, db: Session = Depends(get_db)):
    market = MarketService.get(db, market_id=market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market
