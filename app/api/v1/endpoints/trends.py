from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.price_service import PriceService

router = APIRouter()


@router.get("/history/{commodity_id}")
def get_commodity_history(commodity_id: str, limit: int = 30, db: Session = Depends(get_db)):
    return PriceService.get_commodity_history(db, commodity_id=commodity_id, limit=limit)
