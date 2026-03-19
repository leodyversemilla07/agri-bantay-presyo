from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.schemas.commodity import CommodityCreate


class CommodityService:
    @staticmethod
    def _normalize_name(name: str) -> str:
        return " ".join(name.split())

    @staticmethod
    def _base_query(db: Session, category: Optional[str] = None, search: Optional[str] = None):
        db_query = db.query(Commodity)
        if category:
            db_query = db_query.filter(Commodity.category == category)
        if search:
            db_query = db_query.filter(Commodity.name.ilike(f"%{search}%"))
        return db_query

    @staticmethod
    def get(db: Session, commodity_id: Union[str, UUID]) -> Optional[Commodity]:
        # Convert string to UUID if needed
        if isinstance(commodity_id, str):
            commodity_id = UUID(commodity_id)
        return db.query(Commodity).filter(Commodity.id == commodity_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Commodity]:
        normalized = CommodityService._normalize_name(name)
        return db.query(Commodity).filter(func.lower(Commodity.name) == normalized.lower()).first()

    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Commodity]:
        return CommodityService._base_query(db, category=category, search=search).offset(skip).limit(limit).all()

    @staticmethod
    def count_multi(db: Session, category: Optional[str] = None, search: Optional[str] = None) -> int:
        return CommodityService._base_query(db, category=category, search=search).count()

    @staticmethod
    def create(db: Session, obj_in: CommodityCreate) -> Commodity:
        db_obj = Commodity(
            name=CommodityService._normalize_name(obj_in.name),
            category=obj_in.category,
            variant=obj_in.variant,
            unit=obj_in.unit,
        )
        db.add(db_obj)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_or_create(db: Session, name: str, **kwargs) -> Commodity:
        # Note: name is expected to be already normalized by the caller
        normalized_name = CommodityService._normalize_name(name)
        commodity = CommodityService.get_by_name(db, normalized_name)
        if not commodity:
            db_obj = Commodity(name=normalized_name, **kwargs)
            db.add(db_obj)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                commodity = CommodityService.get_by_name(db, normalized_name)
                if commodity:
                    return commodity
                raise
            db.refresh(db_obj)
            return db_obj
        return commodity

    @staticmethod
    def get_by_names(db: Session, names: List[str]) -> List[Commodity]:
        """Bulk fetch commodities by names."""
        if not names:
            return []
        normalized_names = {CommodityService._normalize_name(name).lower() for name in names}
        return db.query(Commodity).filter(func.lower(Commodity.name).in_(normalized_names)).all()

    @staticmethod
    def search(db: Session, query: str, limit: int = 20) -> List[Commodity]:
        """Search commodities by name (case-insensitive partial match)."""
        normalized = CommodityService._normalize_name(query)
        return db.query(Commodity).filter(Commodity.name.ilike(f"%{normalized}%")).limit(limit).all()
