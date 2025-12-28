from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.market import Market, MarketCreate
from app.services.market_service import MarketService

router = APIRouter()

@router.get("/")
def read_markets(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    from app.models.market import Market
    markets = db.query(Market).offset(skip).limit(limit).all()
    # Explicit conversion to list of dicts to avoid lazy evaluation issues during JSON serialization
    return [{"id": m.id, "name": m.name, "region": m.region, "city": m.city, "is_regional_average": m.is_regional_average} for m in markets]

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
