from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.commodity import Commodity, CommodityCreate
from app.services.commodity_service import CommodityService

router = APIRouter()

from typing import List, Optional


@router.get("/", response_model=List[Commodity])
def read_commodities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
):
    return CommodityService.get_multi(db, skip=skip, limit=limit, category=category)


@router.post("/", response_model=Commodity)
def create_commodity(commodity_in: CommodityCreate, db: Session = Depends(get_db)):
    existing = CommodityService.get_by_name(db, name=commodity_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Commodity already exists")
    return CommodityService.create(db, obj_in=commodity_in)


@router.get("/{commodity_id}", response_model=Commodity)
def read_commodity(commodity_id: str, db: Session = Depends(get_db)):
    commodity = CommodityService.get(db, commodity_id=commodity_id)
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
    return commodity


@router.get("/search/{query}", response_model=List[Commodity])
def search_commodities(query: str, db: Session = Depends(get_db)):
    """Search commodities by name."""
    return CommodityService.search(db, query=query, limit=20)
