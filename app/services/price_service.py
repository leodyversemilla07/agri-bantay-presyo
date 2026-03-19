from datetime import date
from decimal import Decimal
from typing import Any, Dict, Union
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload


class PriceService:
    @staticmethod
    def _coerce_uuid(value: Union[str, UUID, None]) -> UUID | None:
        if value is None or isinstance(value, UUID):
            return value
        return UUID(value)

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.01"))
        return Decimal(str(value)).quantize(Decimal("0.01"))

    @staticmethod
    def get_latest_report_date(db: Session) -> date | None:
        from app.models.price_entry import PriceEntry

        return db.query(func.max(PriceEntry.report_date)).scalar()

    @staticmethod
    def get_previous_report_date(db: Session, current_date: date) -> date | None:
        from app.models.price_entry import PriceEntry

        return (
            db.query(func.max(PriceEntry.report_date))
            .filter(PriceEntry.report_date < current_date)
            .scalar()
        )

    @staticmethod
    def _base_query(db: Session, report_date: date | None = None):
        from app.models.price_entry import PriceEntry

        db_query = (
            db.query(PriceEntry)
            .options(joinedload(PriceEntry.commodity), joinedload(PriceEntry.market))
            .order_by(desc(PriceEntry.report_date))
        )
        if report_date:
            db_query = db_query.filter(PriceEntry.report_date == report_date)
        return db_query

    @staticmethod
    def get_latest_prices(db: Session, skip: int = 0, limit: int = 100):
        latest_report_date = PriceService.get_latest_report_date(db)
        if latest_report_date is None:
            return []
        return PriceService._base_query(db, report_date=latest_report_date).offset(skip).limit(limit).all()

    @staticmethod
    def get_prices_by_date(db: Session, report_date: date, skip: int = 0, limit: int = 100):
        return PriceService._base_query(db, report_date=report_date).offset(skip).limit(limit).all()

    @staticmethod
    def count_prices(db: Session, report_date: date | None = None) -> int:
        if report_date is None:
            report_date = PriceService.get_latest_report_date(db)
            if report_date is None:
                return 0
        return PriceService._base_query(db, report_date=report_date).count()

    @staticmethod
    def get_commodity_history(db: Session, commodity_id: Union[str, UUID], limit: int = 30):
        from app.models.price_entry import PriceEntry

        commodity_id = PriceService._coerce_uuid(commodity_id)
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

        commodity_id = PriceService._coerce_uuid(commodity_id)
        market_id = PriceService._coerce_uuid(market_id)
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

        commodity_id = PriceService._coerce_uuid(commodity_id)
        market_id = PriceService._coerce_uuid(market_id)
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
    def get_snapshot_counts(db: Session, report_date: date) -> dict[str, int]:
        from app.models.price_entry import PriceEntry

        base_query = db.query(PriceEntry).filter(PriceEntry.report_date == report_date)
        return {
            "commodities": base_query.with_entities(func.count(func.distinct(PriceEntry.commodity_id))).scalar() or 0,
            "markets": base_query.with_entities(func.count(func.distinct(PriceEntry.market_id))).scalar() or 0,
            "prices": base_query.count(),
        }

    @staticmethod
    def get_dashboard_snapshot_stats(db: Session) -> dict[str, Any]:
        from app.models.commodity import Commodity
        from app.models.market import Market

        total_commodities = db.query(Commodity).count()
        total_markets = db.query(Market).count()
        latest_report_date = PriceService.get_latest_report_date(db)
        previous_report_date = None
        latest_counts = {"commodities": 0, "markets": 0, "prices": 0}
        previous_counts = None

        if latest_report_date is not None:
            latest_counts = PriceService.get_snapshot_counts(db, latest_report_date)
            previous_report_date = PriceService.get_previous_report_date(db, latest_report_date)
            if previous_report_date is not None:
                previous_counts = PriceService.get_snapshot_counts(db, previous_report_date)

        def _delta(key: str) -> int | None:
            if previous_counts is None:
                return None
            return latest_counts[key] - previous_counts[key]

        return {
            "latest_report_date": latest_report_date,
            "previous_report_date": previous_report_date,
            "commodities": {"count": total_commodities, "change": _delta("commodities")},
            "markets": {"count": total_markets, "change": _delta("markets")},
            "prices": {"count": latest_counts["prices"], "change": _delta("prices")},
        }

    @staticmethod
    def _trend_base_query(db: Session, commodity_id: Union[str, UUID], market_id: Union[str, UUID, None] = None):
        from app.models.price_entry import PriceEntry

        commodity_id = PriceService._coerce_uuid(commodity_id)
        market_id = PriceService._coerce_uuid(market_id)

        query = db.query(
            PriceEntry.report_date.label("report_date"),
            func.avg(PriceEntry.price_prevailing).label("prevailing_price"),
            func.count(func.distinct(PriceEntry.market_id)).label("market_count"),
        ).filter(PriceEntry.commodity_id == commodity_id)

        if market_id is not None:
            query = query.filter(PriceEntry.market_id == market_id)

        return query.group_by(PriceEntry.report_date)

    @staticmethod
    def _trend_subquery(db: Session, commodity_id: Union[str, UUID], market_id: Union[str, UUID, None] = None):
        return PriceService._trend_base_query(db, commodity_id, market_id).subquery()

    @staticmethod
    def get_latest_trend_report_date(
        db: Session,
        commodity_id: Union[str, UUID],
        market_id: Union[str, UUID, None] = None,
    ) -> date | None:
        trend_rows = PriceService._trend_subquery(db, commodity_id, market_id)
        return db.query(func.max(trend_rows.c.report_date)).scalar()

    @staticmethod
    def get_previous_trend_report_date(
        db: Session,
        commodity_id: Union[str, UUID],
        current_date: date,
        market_id: Union[str, UUID, None] = None,
    ) -> date | None:
        trend_rows = PriceService._trend_subquery(db, commodity_id, market_id)
        return (
            db.query(func.max(trend_rows.c.report_date))
            .filter(trend_rows.c.report_date < current_date)
            .scalar()
        )

    @staticmethod
    def get_commodity_trend_snapshot(
        db: Session,
        commodity_id: Union[str, UUID],
        report_date: date,
        market_id: Union[str, UUID, None] = None,
    ) -> dict[str, Any] | None:
        trend_rows = PriceService._trend_subquery(db, commodity_id, market_id)
        row = db.query(trend_rows).filter(trend_rows.c.report_date == report_date).first()
        if not row:
            return None
        return {
            "report_date": row.report_date,
            "prevailing_price": PriceService._to_decimal(row.prevailing_price),
            "market_count": int(row.market_count or 0),
        }

    @staticmethod
    def get_commodity_trend_series(
        db: Session,
        commodity_id: Union[str, UUID],
        market_id: Union[str, UUID, None] = None,
        limit: int = 30,
    ) -> list[dict[str, Any]]:
        trend_rows = PriceService._trend_subquery(db, commodity_id, market_id)
        rows = db.query(trend_rows).order_by(desc(trend_rows.c.report_date)).limit(limit).all()
        return [
            {
                "report_date": row.report_date,
                "prevailing_price": PriceService._to_decimal(row.prevailing_price),
                "market_count": int(row.market_count or 0),
            }
            for row in reversed(rows)
        ]

    @staticmethod
    def get_commodity_trend_summary(
        db: Session,
        commodity_id: Union[str, UUID],
        market_id: Union[str, UUID, None] = None,
        report_date: date | None = None,
    ) -> dict[str, Any] | None:
        commodity_id = PriceService._coerce_uuid(commodity_id)
        market_id = PriceService._coerce_uuid(market_id)
        current_date = report_date or PriceService.get_latest_trend_report_date(db, commodity_id, market_id)
        if current_date is None:
            return None

        current_snapshot = PriceService.get_commodity_trend_snapshot(db, commodity_id, current_date, market_id)
        if current_snapshot is None:
            return None

        previous_date = PriceService.get_previous_trend_report_date(db, commodity_id, current_date, market_id)
        previous_snapshot = None
        if previous_date is not None:
            previous_snapshot = PriceService.get_commodity_trend_snapshot(db, commodity_id, previous_date, market_id)

        current_price = current_snapshot["prevailing_price"]
        previous_price = previous_snapshot["prevailing_price"] if previous_snapshot else None
        absolute_change = None
        percent_change = None

        if current_price is not None and previous_price is not None:
            absolute_change = (current_price - previous_price).quantize(Decimal("0.01"))
            if previous_price != 0:
                percent_change = round(float((absolute_change / previous_price) * 100), 1)

        return {
            "commodity_id": commodity_id,
            "market_id": market_id,
            "latest_report_date": current_date,
            "previous_report_date": previous_date,
            "current_prevailing_price": current_price,
            "previous_prevailing_price": previous_price,
            "absolute_change": absolute_change,
            "percent_change": percent_change,
            "market_count": current_snapshot["market_count"],
        }

    @staticmethod
    def create_entry(db: Session, data: Dict[str, Any]):
        from app.models.price_entry import PriceEntry

        identity_filter = (
            PriceEntry.commodity_id == data["commodity_id"],
            PriceEntry.market_id == data["market_id"],
            PriceEntry.report_date == data["report_date"],
            PriceEntry.report_type == data["report_type"],
        )

        # Check for existing entry to prevent duplicates
        existing = db.query(PriceEntry).filter(*identity_filter).first()

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
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = db.query(PriceEntry).filter(*identity_filter).first()
            if not existing:
                raise
            for key, value in data.items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        db.refresh(db_obj)
        return db_obj
