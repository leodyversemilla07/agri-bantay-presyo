from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price_entry import PriceEntry
from app.models.supply_index import SupplyIndex


def _commodity_weight(commodity: Commodity):
    return (len(commodity.price_entries) + len(commodity.supply_indices), commodity.name.lower(), str(commodity.id))


def _market_weight(market: Market):
    return (len(market.price_entries), market.name.lower(), str(market.id))


def _price_entry_weight(entry: PriceEntry):
    populated_fields = sum(
        value is not None
        for value in [
            entry.price_low,
            entry.price_high,
            entry.price_prevailing,
            entry.price_average,
            entry.period_start,
            entry.period_end,
            entry.source_file,
        ]
    )
    return (populated_fields, str(entry.id))


class DataIntegrityService:
    @staticmethod
    def find_duplicate_commodities(db: Session):
        duplicate_keys = (
            db.query(func.lower(Commodity.name))
            .group_by(func.lower(Commodity.name))
            .having(func.count(Commodity.id) > 1)
            .all()
        )
        duplicates = []
        for (normalized_name,) in duplicate_keys:
            items = (
                db.query(Commodity)
                .filter(func.lower(Commodity.name) == normalized_name)
                .order_by(Commodity.name.asc())
                .all()
            )
            canonical = max(items, key=_commodity_weight)
            duplicates.append({"normalized_name": normalized_name, "canonical": canonical, "duplicates": items})
        return duplicates

    @staticmethod
    def find_duplicate_markets(db: Session):
        duplicate_keys = (
            db.query(func.lower(Market.name))
            .group_by(func.lower(Market.name))
            .having(func.count(Market.id) > 1)
            .all()
        )
        duplicates = []
        for (normalized_name,) in duplicate_keys:
            items = db.query(Market).filter(func.lower(Market.name) == normalized_name).order_by(Market.name.asc()).all()
            canonical = max(items, key=_market_weight)
            duplicates.append({"normalized_name": normalized_name, "canonical": canonical, "duplicates": items})
        return duplicates

    @staticmethod
    def find_duplicate_price_entries(db: Session):
        duplicate_keys = (
            db.query(
                PriceEntry.commodity_id,
                PriceEntry.market_id,
                PriceEntry.report_date,
                PriceEntry.report_type,
            )
            .group_by(
                PriceEntry.commodity_id,
                PriceEntry.market_id,
                PriceEntry.report_date,
                PriceEntry.report_type,
            )
            .having(func.count(PriceEntry.id) > 1)
            .all()
        )
        duplicates = []
        for commodity_id, market_id, report_date, report_type in duplicate_keys:
            items = (
                db.query(PriceEntry)
                .filter(
                    PriceEntry.commodity_id == commodity_id,
                    PriceEntry.market_id == market_id,
                    PriceEntry.report_date == report_date,
                    PriceEntry.report_type == report_type,
                )
                .order_by(PriceEntry.id.asc())
                .all()
            )
            canonical = max(items, key=_price_entry_weight)
            duplicates.append(
                {
                    "commodity_id": commodity_id,
                    "market_id": market_id,
                    "report_date": report_date,
                    "report_type": report_type,
                    "canonical": canonical,
                    "duplicates": items,
                }
            )
        return duplicates

    @staticmethod
    def generate_duplicate_report(db: Session):
        commodity_duplicates = DataIntegrityService.find_duplicate_commodities(db)
        market_duplicates = DataIntegrityService.find_duplicate_markets(db)
        price_entry_duplicates = DataIntegrityService.find_duplicate_price_entries(db)
        return {
            "commodity_duplicates": commodity_duplicates,
            "market_duplicates": market_duplicates,
            "price_entry_duplicates": price_entry_duplicates,
        }

    @staticmethod
    def cleanup_duplicates(db: Session):
        report = DataIntegrityService.generate_duplicate_report(db)
        cleanup_summary = defaultdict(int)

        for group in report["commodity_duplicates"]:
            canonical = group["canonical"]
            for item in group["duplicates"]:
                if item.id == canonical.id:
                    continue
                db.query(PriceEntry).filter(PriceEntry.commodity_id == item.id).update(
                    {"commodity_id": canonical.id},
                    synchronize_session=False,
                )
                db.query(SupplyIndex).filter(SupplyIndex.commodity_id == item.id).update(
                    {"commodity_id": canonical.id},
                    synchronize_session=False,
                )
                db.delete(item)
                cleanup_summary["commodities_merged"] += 1

        for group in report["market_duplicates"]:
            canonical = group["canonical"]
            for item in group["duplicates"]:
                if item.id == canonical.id:
                    continue
                db.query(PriceEntry).filter(PriceEntry.market_id == item.id).update(
                    {"market_id": canonical.id},
                    synchronize_session=False,
                )
                db.delete(item)
                cleanup_summary["markets_merged"] += 1

        for group in report["price_entry_duplicates"]:
            canonical = group["canonical"]
            for item in group["duplicates"]:
                if item.id == canonical.id:
                    continue
                db.delete(item)
                cleanup_summary["price_entries_deleted"] += 1

        db.commit()
        return dict(cleanup_summary)
