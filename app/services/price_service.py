from datetime import date
from typing import Any, Dict, Union
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload


class PriceService:
    @staticmethod
    def get_latest_prices(db: Session, skip: int = 0, limit: int = 100):
        from app.models.price_entry import PriceEntry

        return (
            db.query(PriceEntry)
            .options(joinedload(PriceEntry.commodity), joinedload(PriceEntry.market))
            .order_by(desc(PriceEntry.report_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_prices_by_date(db: Session, report_date: date):
        from app.models.price_entry import PriceEntry

        return (
            db.query(PriceEntry)
            .options(joinedload(PriceEntry.commodity), joinedload(PriceEntry.market))
            .filter(PriceEntry.report_date == report_date)
            .all()
        )

    @staticmethod
    def get_commodity_history(db: Session, commodity_id: Union[str, UUID], limit: int = 30):
        from app.models.price_entry import PriceEntry

        # Convert string to UUID if needed
        if isinstance(commodity_id, str):
            commodity_id = UUID(commodity_id)
        return (
            db.query(PriceEntry)
            .filter(PriceEntry.commodity_id == commodity_id)
            .order_by(desc(PriceEntry.report_date))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_previous_price(
        db: Session,
        commodity_id: Union[str, UUID],
        market_id: Union[str, UUID],
        current_date: date,
    ):
        from app.models.price_entry import PriceEntry

        # Convert strings to UUID if needed
        if isinstance(commodity_id, str):
            commodity_id = UUID(commodity_id)
        if isinstance(market_id, str):
            market_id = UUID(market_id)
        return (
            db.query(PriceEntry)
            .filter(
                PriceEntry.commodity_id == commodity_id,
                PriceEntry.market_id == market_id,
                PriceEntry.report_date < current_date,
            )
            .order_by(desc(PriceEntry.report_date))
            .first()
        )

    @staticmethod
    def get_price_change(
        db: Session,
        commodity_id: Union[str, UUID],
        market_id: Union[str, UUID],
        current_date: date,
    ):
        from app.models.price_entry import PriceEntry

        # Convert strings to UUID if needed
        if isinstance(commodity_id, str):
            commodity_id = UUID(commodity_id)
        if isinstance(market_id, str):
            market_id = UUID(market_id)
        current = (
            db.query(PriceEntry)
            .filter(
                PriceEntry.commodity_id == commodity_id,
                PriceEntry.market_id == market_id,
                PriceEntry.report_date == current_date,
            )
            .first()
        )

        if not current:
            return 0

        previous = PriceService.get_previous_price(db, commodity_id, market_id, current_date)

        if not previous or not previous.price_prevailing:
            return 0

        current_price = current.price_prevailing or 0
        prev_price = previous.price_prevailing or 0

        if prev_price == 0:
            return 0

        return round(((current_price - prev_price) / prev_price) * 100, 1)

    @staticmethod
    def create_entry(db: Session, data: Dict[str, Any]):
        from app.models.price_entry import PriceEntry

        # Check for existing entry to prevent duplicates
        existing = (
            db.query(PriceEntry)
            .filter(
                PriceEntry.commodity_id == data["commodity_id"],
                PriceEntry.market_id == data["market_id"],
                PriceEntry.report_date == data["report_date"],
                PriceEntry.report_type == data["report_type"],
            )
            .first()
        )

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
