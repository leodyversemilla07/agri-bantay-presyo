from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import verify_service_api_key
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.commodity import Commodity, CommodityCreate
from app.schemas.pagination import PaginatedResponse
from app.schemas.price_entry import PriceEntry
from app.services.commodity_service import CommodityService
from app.services.price_service import PriceService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[Commodity])
@limiter.limit("200/minute")
def read_commodities(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    q: Optional[str] = Query(None, description="Case-insensitive commodity name search"),
):
    items = CommodityService.get_multi(db, skip=skip, limit=limit, category=category, search=q)
    total = CommodityService.count_multi(db, category=category, search=q)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/", response_model=Commodity, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_commodity(
    request: Request,
    response: Response,
    commodity_in: CommodityCreate,
    db: Session = Depends(get_db),
    _=Depends(verify_service_api_key),
):
    existing = CommodityService.get_by_name(db, name=commodity_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Commodity already exists")
    commodity = CommodityService.create(db, obj_in=commodity_in)
    response.headers["Location"] = f"{settings.API_V1_STR}/commodities/{commodity.id}"
    return commodity


@router.get("/{commodity_id}", response_model=Commodity)
@limiter.limit("200/minute")
def read_commodity(request: Request, commodity_id: UUID, db: Session = Depends(get_db)):
    commodity = CommodityService.get(db, commodity_id=commodity_id)
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
    return commodity


@router.get("/{commodity_id}/history", response_model=List[PriceEntry])
@limiter.limit("100/minute")
def read_commodity_history(
    request: Request,
    commodity_id: UUID,
    limit: int = 30,
    db: Session = Depends(get_db),
):
    """Return price history nested under the commodity resource."""
    return PriceService.get_commodity_history(db, commodity_id=commodity_id, limit=limit)


@router.get("/search/{query}", response_model=List[Commodity], include_in_schema=False)
@limiter.limit("100/minute")
def search_commodities(request: Request, query: str, db: Session = Depends(get_db)):
    """Legacy alias for commodity search."""
    return CommodityService.get_multi(db, limit=20, search=query)
