import argparse
import json
import os
import sys
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.price_entry import PriceEntry
from app.scraper.source import MonitoringSource
from app.scraper.tasks import scrape_daily_prices


def _resolve_links(urls: list[str], start_date: date | None, end_date: date | None) -> list[str]:
    if urls:
        return urls
    if start_date is None:
        raise ValueError("Provide --url or a date range with --start-date/--end-date")
    if end_date is None:
        end_date = start_date

    links = MonitoringSource.get_latest_pdf_links()
    return MonitoringSource.filter_links_by_date_range(links, start_date, end_date)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill Daily Retail Price PDFs into the local database.")
    parser.add_argument("--start-date", type=date.fromisoformat, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", type=date.fromisoformat, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--url", action="append", default=[], help="Explicit PDF URL to ingest. Repeatable.")
    parser.add_argument("--force", action="store_true", help="Reprocess files even if they already exist in the DB.")
    args = parser.parse_args()

    links = _resolve_links(args.url, args.start_date, args.end_date)
    db = SessionLocal()
    try:
        processed_files = {
            row[0]
            for row in db.query(PriceEntry.source_file).distinct().all()
            if row[0]
        }
    finally:
        db.close()

    if not args.force:
        links = [url for url in links if url.split("/")[-1] not in processed_files]

    results = []
    for url in links:
        result = scrape_daily_prices.apply(args=[url]).get()
        results.append(result)

    print(json.dumps({"requested": len(links), "results": results}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
