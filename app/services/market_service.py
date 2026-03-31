from typing import Union
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas.market import MarketCreate


class MarketService:
    @staticmethod
    def _normalize_name(name: str) -> str:
        return " ".join(name.split())

    @staticmethod
    def _base_query(db: Session, query: str | None = None):
        from app.models.market import Market

        db_query = db.query(Market)
        if query:
            db_query = db_query.filter(Market.name.ilike(f"%{query}%"))
        return db_query

    @staticmethod
    def get(db: Session, market_id: Union[str, UUID]):
        from app.models.market import Market

        # Convert string to UUID if needed
        if isinstance(market_id, str):
            market_id = UUID(market_id)
        return db.query(Market).filter(Market.id == market_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str):
        from app.models.market import Market

        normalized = MarketService._normalize_name(name)
        return db.query(Market).filter(func.lower(Market.name) == normalized.lower()).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100, query: str | None = None):
        return MarketService._base_query(db, query=query).offset(skip).limit(limit).all()

    @staticmethod
    def count_multi(db: Session, query: str | None = None) -> int:
        return MarketService._base_query(db, query=query).count()

    @staticmethod
    def create(db: Session, obj_in: MarketCreate):
        from app.models.market import Market

        db_obj = Market(
            name=MarketService._normalize_name(obj_in.name),
            region=obj_in.region,
            city=obj_in.city,
            is_regional_average=obj_in.is_regional_average,
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
    def get_or_create(db: Session, name: str, **kwargs):
        from app.models.market import Market

        normalized_name = MarketService._normalize_name(name)
        market = MarketService.get_by_name(db, normalized_name)
        if not market:
            db_obj = Market(name=normalized_name, **kwargs)
            db.add(db_obj)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                market = MarketService.get_by_name(db, normalized_name)
                if market:
                    return market
                raise
            db.refresh(db_obj)
            return db_obj
        return market

    @staticmethod
    def search(db: Session, query: str, limit: int = 20):
        """Search markets by name (case-insensitive partial match)."""
        from app.models.market import Market

        normalized = MarketService._normalize_name(query)
        return db.query(Market).filter(Market.name.ilike(f"%{normalized}%")).limit(limit).all()
