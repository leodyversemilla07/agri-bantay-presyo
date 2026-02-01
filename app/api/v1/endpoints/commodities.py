from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.commodity import Commodity, CommodityCreate
from app.services.commodity_service import CommodityService

router = APIRouter()


@router.get("/", response_model=List[Commodity])
@limiter.limit("200/minute")
def read_commodities(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
):
    return CommodityService.get_multi(db, skip=skip, limit=limit, category=category)


@router.post("/", response_model=Commodity)
@limiter.limit("30/minute")
def create_commodity(
    request: Request,
    commodity_in: CommodityCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    existing = CommodityService.get_by_name(db, name=commodity_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Commodity already exists")
    return CommodityService.create(db, obj_in=commodity_in)


@router.get("/{commodity_id}", response_model=Commodity)
@limiter.limit("200/minute")
def read_commodity(request: Request, commodity_id: str, db: Session = Depends(get_db)):
    commodity = CommodityService.get(db, commodity_id=commodity_id)
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
    return commodity


@router.get("/search/{query}", response_model=List[Commodity])
@limiter.limit("100/minute")
def search_commodities(request: Request, query: str, db: Session = Depends(get_db)):
    """Search commodities by name."""
    return CommodityService.search(db, query=query, limit=20)
