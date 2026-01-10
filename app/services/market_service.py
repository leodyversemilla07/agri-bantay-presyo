from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.market import MarketCreate, MarketUpdate


class MarketService:
    @staticmethod
    def get(db: Session, market_id: str):
        from app.models.market import Market

        return db.query(Market).filter(Market.id == market_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str):
        from app.models.market import Market

        return db.query(Market).filter(Market.name == name).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100):
        from app.models.market import Market

        return db.query(Market).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, obj_in: MarketCreate):
        from app.models.market import Market

        db_obj = Market(name=obj_in.name, region=obj_in.region, city=obj_in.city)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_or_create(db: Session, name: str, **kwargs):
        from app.models.market import Market

        market = MarketService.get_by_name(db, name)
        if not market:
            db_obj = Market(name=name, **kwargs)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        return market

    @staticmethod
    def search(db: Session, query: str, limit: int = 20):
        """Search markets by name (case-insensitive partial match)."""
        from app.models.market import Market

        return (
            db.query(Market).filter(Market.name.ilike(f"%{query}%")).limit(limit).all()
        )
