import logging
import os
from datetime import date, datetime

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.exceptions import PDFDownloadError, PDFParseError
from app.db.session import SessionLocal
from app.scraper.downloader import PDFDownloader
from app.scraper.parser import PriceParser
from app.services.commodity_service import CommodityService
from app.services.market_service import MarketService
from app.services.price_service import PriceService

logger = logging.getLogger(__name__)


def _normalize_report_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None
    return None


@celery_app.task(
    name="app.scraper.tasks.scrape_daily_prices",
    bind=True,
    autoretry_for=(PDFDownloadError, ConnectionError),
    retry_backoff=True,
    retry_backoff_max=600,  # Max 10 minutes between retries
    retry_kwargs={"max_retries": 3},
    acks_late=True,  # Acknowledge after task completes
)
def scrape_daily_prices(self, url: str):
    """
    Scrape daily prices from a PDF URL.

    Features:
    - Automatic retry on download failures (up to 3 times with exponential backoff)
    - Proper cleanup of downloaded files
    - Detailed logging for debugging
    """
    downloader = PDFDownloader()
    parser = PriceParser()
    db = SessionLocal()
    pdf_path = None
    entries_processed = 0

    try:
        logger.info(f"Starting daily scrape for URL: {url} (attempt {self.request.retries + 1})")

        # Download PDF with error handling
        try:
            pdf_path = downloader.download_pdf_sync(url)
        except Exception as e:
            raise PDFDownloadError(url=url, reason=str(e))

        # Parse PDF deterministically
        try:
            parsed_results = parser.parse_daily_prevailing(str(pdf_path))
        except Exception as e:
            raise PDFParseError(filename=pdf_path.name if pdf_path else url, reason=str(e))

        if not parsed_results:
            logger.warning(f"No data extracted from {pdf_path.name if pdf_path else url}")
            return {"status": "empty", "url": url, "entries": 0}

        # Pre-process entries to normalize names and identify unique commodities
        unique_commodity_names = set()
        name_to_sample_entry = {}

        for entry in parsed_results:
            raw_name = entry.get("commodity", "Unknown")
            normalized_name = parser.normalization_map.get(raw_name, raw_name)
            entry["_normalized_name"] = normalized_name
            unique_commodity_names.add(normalized_name)
            if normalized_name not in name_to_sample_entry:
                name_to_sample_entry[normalized_name] = entry

        # Bulk fetch existing commodities
        existing_commodities = CommodityService.get_by_names(db, list(unique_commodity_names))
        commodity_map = {c.name: c for c in existing_commodities}

        # Create missing commodities
        for name in unique_commodity_names:
            if name not in commodity_map:
                try:
                    sample = name_to_sample_entry[name]
                    new_commodity = CommodityService.get_or_create(
                        db,
                        name=name,
                        category=sample.get("category"),
                        unit=sample.get("unit"),
                    )
                    commodity_map[name] = new_commodity
                except Exception as e:
                    logger.error(f"Failed to create commodity {name}: {e}")

        # Process each entry with individual error handling
        errors = []
        for entry in parsed_results:
            try:
                raw_name = entry.get("commodity", "Unknown")
                normalized_name = entry.get("_normalized_name")

                commodity = commodity_map.get(normalized_name)
                if not commodity:
                    raise ValueError(f"Commodity {normalized_name} unavailable")

                # Use configurable default market from settings
                market_name = entry.get("market", settings.DEFAULT_MARKET_NAME)
                market = MarketService.get_or_create(db, name=market_name)

                report_date = _normalize_report_date(entry.get("report_date"))
                if report_date is None:
                    raise ValueError("Invalid report_date (expected ISO date or date object)")

                PriceService.create_entry(
                    db,
                    {
                        "commodity_id": commodity.id,
                        "market_id": market.id,
                        "report_date": report_date,
                        "price_low": entry.get("price_low"),
                        "price_high": entry.get("price_high"),
                        "price_prevailing": entry.get("price_prevailing"),
                        "price_average": entry.get("price_average"),
                        "report_type": entry.get("report_type", "DAILY_RETAIL"),
                        "source_file": pdf_path.name if pdf_path else url.split("/")[-1],
                    },
                )
                entries_processed += 1

            except Exception as entry_error:
                entry_name = entry.get("commodity", "Unknown")
                errors.append({"commodity": entry_name, "error": str(entry_error)})
                logger.warning(f"Failed to process entry {entry_name}: {entry_error}")
                continue  # Continue processing other entries

        logger.info(
            f"Successfully processed {entries_processed}/{len(parsed_results)} entries from {pdf_path.name if pdf_path else url}"
        )

        if errors:
            logger.warning(f"Encountered {len(errors)} errors during processing")

        # Clean up downloaded file
        if pdf_path and pdf_path.exists():
            os.remove(pdf_path)
            logger.info(f"Cleaned up downloaded file: {pdf_path.name}")

        return {
            "status": "success",
            "url": url,
            "entries_processed": entries_processed,
            "entries_total": len(parsed_results),
            "errors": len(errors),
        }

    except (PDFDownloadError, PDFParseError) as e:
        logger.error(f"Scraping failed (will retry): {e.message}")
        # Clean up on failure
        if pdf_path and pdf_path.exists():
            os.remove(pdf_path)
        raise  # Let Celery handle retry

    except Exception as e:
        logger.exception(f"Unexpected error during scraping: {e}")
        # Clean up on failure
        if pdf_path and pdf_path.exists():
            os.remove(pdf_path)
        raise

    finally:
        db.close()
