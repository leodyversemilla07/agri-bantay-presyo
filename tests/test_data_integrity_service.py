from sqlalchemy import text

from app.models.commodity import Commodity
from app.models.market import Market
from app.services.data_integrity_service import DataIntegrityService


def test_duplicate_report_detects_case_insensitive_name_collisions(db_session):
    db_session.execute(text("DROP INDEX uq_commodities_name_ci"))
    db_session.execute(text("DROP INDEX uq_markets_name_ci"))
    db_session.commit()

    db_session.add_all(
        [
            Commodity(name="Bangus", category="Fish"),
            Commodity(name="bangus", category="Fish"),
            Market(name="Divisoria Market", region="NCR"),
            Market(name="divisoria market", region="NCR"),
        ]
    )
    db_session.commit()

    report = DataIntegrityService.generate_duplicate_report(db_session)

    assert len(report["commodity_duplicates"]) == 1
    assert len(report["market_duplicates"]) == 1
    assert report["price_entry_duplicates"] == []


def test_cleanup_duplicates_merges_case_insensitive_name_collisions(db_session):
    db_session.execute(text("DROP INDEX uq_commodities_name_ci"))
    db_session.execute(text("DROP INDEX uq_markets_name_ci"))
    db_session.commit()

    db_session.add_all(
        [
            Commodity(name="Bangus", category="Fish"),
            Commodity(name="bangus", category="Fish"),
            Market(name="Divisoria Market", region="NCR"),
            Market(name="divisoria market", region="NCR"),
        ]
    )
    db_session.commit()

    summary = DataIntegrityService.cleanup_duplicates(db_session)

    assert summary["commodities_merged"] == 1
    assert summary["markets_merged"] == 1
    assert db_session.query(Commodity).count() == 1
    assert db_session.query(Market).count() == 1
