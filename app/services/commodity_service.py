from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.schemas.commodity import CommodityCreate


class CommodityService:
    @staticmethod
    def get(db: Session, commodity_id: Union[str, UUID]) -> Optional[Commodity]:
        # Convert string to UUID if needed
        if isinstance(commodity_id, str):
            commodity_id = UUID(commodity_id)
        return db.query(Commodity).filter(Commodity.id == commodity_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Commodity]:
        return db.query(Commodity).filter(Commodity.name == name).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> List[Commodity]:
        query = db.query(Commodity)
        if category:
            query = query.filter(Commodity.category == category)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, obj_in: CommodityCreate) -> Commodity:
        db_obj = Commodity(
            name=obj_in.name,
            category=obj_in.category,
            variant=obj_in.variant,
            unit=obj_in.unit,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_or_create(db: Session, name: str, **kwargs) -> Commodity:
        # Note: name is expected to be already normalized by the caller
        commodity = CommodityService.get_by_name(db, name)
        if not commodity:
            db_obj = Commodity(name=name, **kwargs)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        return commodity

    @staticmethod
    def get_by_names(db: Session, names: List[str]) -> List[Commodity]:
        """Bulk fetch commodities by names."""
        if not names:
            return []
        return db.query(Commodity).filter(Commodity.name.in_(names)).all()

    @staticmethod
    def search(db: Session, query: str, limit: int = 20) -> List[Commodity]:
        """Search commodities by name (case-insensitive partial match)."""
        return db.query(Commodity).filter(Commodity.name.ilike(f"%{query}%")).limit(limit).all()
