from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import date

class PriceService:
    @staticmethod
    def get_latest_prices(db: Session, limit: int = 100):
        from app.models.price_entry import PriceEntry
        return db.query(PriceEntry).options(
            joinedload(PriceEntry.commodity),
            joinedload(PriceEntry.market)
        ).order_by(desc(PriceEntry.report_date)).limit(limit).all()

    @staticmethod
    def get_prices_by_date(db: Session, report_date: date):
        from app.models.price_entry import PriceEntry
        return db.query(PriceEntry).options(
            joinedload(PriceEntry.commodity),
            joinedload(PriceEntry.market)
        ).filter(PriceEntry.report_date == report_date).all()

    @staticmethod
    def get_commodity_history(db: Session, commodity_id: str, limit: int = 30):
        from app.models.price_entry import PriceEntry
        return db.query(PriceEntry).filter(
            PriceEntry.commodity_id == commodity_id
        ).order_by(desc(PriceEntry.report_date)).limit(limit).all()

    @staticmethod
    def create_entry(db: Session, data: Dict[str, Any]):
        from app.models.price_entry import PriceEntry
        # Check for existing entry to prevent duplicates
        existing = db.query(PriceEntry).filter(
            PriceEntry.commodity_id == data["commodity_id"],
            PriceEntry.market_id == data["market_id"],
            PriceEntry.report_date == data["report_date"],
            PriceEntry.report_type == data["report_type"]
        ).first()

        if existing:
            # Update existing record
            for key, value in data.items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing

        # Create new record
        db_obj = PriceEntry(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
