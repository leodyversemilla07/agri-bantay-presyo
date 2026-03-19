from datetime import date

from app.models.ingestion_run import IngestionRun
from app.scraper.discovery import discover_and_scrape
from app.scraper.tasks import scrape_daily_prices


def _session_factory(bind):
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(autocommit=False, autoflush=False, bind=bind)
    return Session


def test_scrape_task_records_successful_ingestion_run(db_session, monkeypatch, tmp_path):
    session_factory = _session_factory(db_session.bind)
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")

    monkeypatch.setattr("app.scraper.tasks.SessionLocal", session_factory)
    monkeypatch.setattr("app.scraper.tasks.PDFDownloader.download_pdf_sync", lambda self, url: pdf_path)
    monkeypatch.setattr(
        "app.scraper.tasks.PriceParser.parse_daily_prevailing",
        lambda self, path: [
            {
                "commodity": "Bangus",
                "category": "Fish",
                "unit": "kg",
                "market": "Test Market",
                "price_low": 100.0,
                "price_high": 120.0,
                "price_prevailing": 110.0,
                "price_average": None,
                "report_date": date(2025, 1, 20),
                "report_type": "DAILY_RETAIL",
            }
        ],
    )

    result = scrape_daily_prices.apply(args=["https://example.com/sample.pdf"]).get()

    verification_session = session_factory()
    try:
        run = verification_session.query(IngestionRun).one()
        assert result["status"] == "success"
        assert run.task_name == "scrape_daily_prices"
        assert run.status == "success"
        assert run.report_date == date(2025, 1, 20)
        assert run.entries_processed == 1
        assert run.error_count == 0
    finally:
        verification_session.close()


def test_scrape_task_records_failed_ingestion_run(db_session, monkeypatch):
    session_factory = _session_factory(db_session.bind)
    monkeypatch.setattr("app.scraper.tasks.SessionLocal", session_factory)

    def _raise_download_error(self, url):
        from app.core.exceptions import PDFDownloadError

        raise PDFDownloadError(url=url, reason="network down")

    monkeypatch.setattr("app.scraper.tasks.PDFDownloader.download_pdf_sync", _raise_download_error)

    result = scrape_daily_prices.apply(args=["https://example.com/sample.pdf"])

    verification_session = session_factory()
    try:
        run = verification_session.query(IngestionRun).one()
        assert result.failed()
        assert run.status == "failed"
        assert "Failed to download PDF" in run.error_message
    finally:
        verification_session.close()


def test_discovery_task_records_run(db_session, monkeypatch):
    session_factory = _session_factory(db_session.bind)
    delay_calls = []

    monkeypatch.setattr("app.scraper.discovery.SessionLocal", session_factory)
    monkeypatch.setattr("app.scraper.discovery.get_processed_files", lambda: [])
    monkeypatch.setattr(
        "app.scraper.discovery.MonitoringSource.get_new_pdf_links",
        lambda processed_files: ["https://example.com/a.pdf"],
    )
    monkeypatch.setattr("app.scraper.discovery.scrape_daily_prices.delay", lambda url: delay_calls.append(url))

    result = discover_and_scrape.apply().get()

    verification_session = session_factory()
    try:
        run = verification_session.query(IngestionRun).one()
        assert result["status"] == "success"
        assert run.task_name == "discover_and_scrape"
        assert run.status == "success"
        assert run.entries_processed == 1
        assert delay_calls == ["https://example.com/a.pdf"]
    finally:
        verification_session.close()
