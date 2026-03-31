import logging
import os
import time
from datetime import date, datetime
from statistics import median

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.exceptions import PDFDownloadError, PDFParseError
from app.db.session import SessionLocal
from app.scraper.downloader import PDFDownloader
from app.scraper.parser import PriceParser
from app.services.commodity_service import CommodityService
from app.services.ingestion_run_service import IngestionRunService
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


def _normalize_name(value: str | None, default: str = "Unknown") -> str:
    return " ".join((value or default).split())


def _build_anomaly_flags(db, parsed_results, report_date):
    anomaly_flags: list[str] = []

    if report_date is None:
        anomaly_flags.append("missing_report_date")

    seen = set()
    duplicate_count = 0
    for entry in parsed_results:
        identity = (
            _normalize_name(entry.get("_normalized_name") or entry.get("commodity")).lower(),
            _normalize_name(entry.get("market"), settings.DEFAULT_MARKET_NAME).lower(),
            str(_normalize_report_date(entry.get("report_date"))),
            entry.get("report_type", "DAILY_RETAIL"),
        )
        if identity in seen:
            duplicate_count += 1
        else:
            seen.add(identity)
    if duplicate_count:
        anomaly_flags.append(f"duplicate_entries_in_source:{duplicate_count}")

    missing_prevailing_count = sum(1 for entry in parsed_results if entry.get("price_prevailing") is None)
    if parsed_results:
        missing_ratio = missing_prevailing_count / len(parsed_results)
        if missing_ratio >= settings.INGESTION_ANOMALY_MISSING_PREVAILING_RATIO_THRESHOLD:
            anomaly_flags.append(
                f"high_missing_prevailing_ratio:{missing_prevailing_count}/{len(parsed_results)}"
            )

    baseline_runs = IngestionRunService.get_recent_successful_scrapes(
        db,
        limit=settings.INGESTION_ANOMALY_LOOKBACK_RUNS,
    )
    baseline_counts = [run.entries_total for run in baseline_runs if run.entries_total]
    if baseline_counts:
        baseline_median = int(median(baseline_counts))
        threshold = max(1, int(baseline_median * settings.INGESTION_ANOMALY_ROW_COUNT_RATIO_THRESHOLD))
        if len(parsed_results) < threshold:
            anomaly_flags.append(f"low_row_count:{len(parsed_results)}<baseline_threshold:{threshold}")

    return anomaly_flags


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
    entries_inserted = 0
    entries_updated = 0
    entries_skipped = 0
    run = IngestionRunService.start_run(
        db,
        task_name="scrape_daily_prices",
        task_id=self.request.id,
        source_url=url,
        source_file=url.split("/")[-1],
    )
    report_date = None

    try:
        started_at = time.monotonic()
        logger.info(
            "Starting daily scrape",
            extra={
                "event": "scrape_started",
                "task_id": self.request.id,
                "task_name": "scrape_daily_prices",
                "source_url": url,
                "source_file": url.split("/")[-1],
            },
        )

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
            logger.warning(
                "No data extracted from source PDF",
                extra={
                    "event": "scrape_empty",
                    "task_id": self.request.id,
                    "source_url": url,
                    "source_file": pdf_path.name if pdf_path else url.split("/")[-1],
                },
            )
            IngestionRunService.finish_run(
                db,
                run,
                status="empty",
                entries_total=0,
                entries_processed=0,
                error_count=0,
            )
            return {"status": "empty", "url": url, "entries": 0}

        report_date = _normalize_report_date(parsed_results[0].get("report_date"))
        anomaly_flags = _build_anomaly_flags(db, parsed_results, report_date)

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
                except Exception:
                    logger.error(
                        "Failed to create commodity during scrape",
                        extra={
                            "event": "commodity_create_failed",
                            "task_id": self.request.id,
                            "source_url": url,
                        },
                    )

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
                market = MarketService.get_by_name(db, market_name)
                if market is None:
                    market = MarketService.get_or_create(db, name=market_name)

                report_date = _normalize_report_date(entry.get("report_date"))
                if report_date is None:
                    raise ValueError("Invalid report_date (expected ISO date or date object)")

                _, action = PriceService.upsert_entry(
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
                if action == "inserted":
                    entries_inserted += 1
                elif action == "updated":
                    entries_updated += 1
                else:
                    entries_skipped += 1

            except Exception as entry_error:
                entry_name = entry.get("commodity", "Unknown")
                errors.append({"commodity": entry_name, "error": str(entry_error)})
                logger.warning(
                    "Failed to process scraped entry",
                    extra={
                        "event": "scrape_entry_failed",
                        "task_id": self.request.id,
                        "source_url": url,
                        "source_file": pdf_path.name if pdf_path else url.split("/")[-1],
                    },
                )
                continue  # Continue processing other entries
        anomaly_flags = list(dict.fromkeys(anomaly_flags))

        logger.info(
            "Daily scrape completed",
            extra={
                "event": "scrape_completed",
                "task_id": self.request.id,
                "task_name": "scrape_daily_prices",
                "source_url": url,
                "source_file": pdf_path.name if pdf_path else url.split("/")[-1],
                "report_date": report_date,
                "status": "success" if not errors else "partial_success",
                "entries_total": len(parsed_results),
                "entries_processed": entries_processed,
                "entries_inserted": entries_inserted,
                "entries_updated": entries_updated,
                "entries_skipped": entries_skipped,
                "error_count": len(errors),
                "anomaly_count": len(anomaly_flags),
                "anomaly_flags": anomaly_flags,
                "elapsed_seconds": round(time.monotonic() - started_at, 3),
            },
        )

        if errors:
            logger.warning(
                "Scrape completed with entry-level errors",
                extra={
                    "event": "scrape_completed_with_errors",
                    "task_id": self.request.id,
                    "source_url": url,
                    "error_count": len(errors),
                },
            )

        IngestionRunService.finish_run(
            db,
            run,
            status="success" if not errors else "partial_success",
            report_date=report_date,
            entries_total=len(parsed_results),
            entries_processed=entries_processed,
            entries_inserted=entries_inserted,
            entries_updated=entries_updated,
            entries_skipped=entries_skipped,
            error_count=len(errors),
            anomaly_count=len(anomaly_flags),
            anomaly_flags=anomaly_flags,
            error_message=None if not errors else f"{len(errors)} entries failed during processing",
        )

        # Clean up downloaded file
        if pdf_path and pdf_path.exists():
            os.remove(pdf_path)
            logger.info(
                "Cleaned up downloaded PDF",
                extra={
                    "event": "scrape_cleanup_completed",
                    "task_id": self.request.id,
                    "source_file": pdf_path.name,
                },
            )

        return {
            "status": "success",
            "url": url,
            "entries_processed": entries_processed,
            "entries_total": len(parsed_results),
            "errors": len(errors),
        }

    except (PDFDownloadError, PDFParseError) as e:
        logger.error(
            "Scraping failed and will be retried",
            extra={
                "event": "scrape_failed_retryable",
                "task_id": self.request.id,
                "task_name": "scrape_daily_prices",
                "source_url": url,
                "source_file": pdf_path.name if pdf_path else url.split("/")[-1],
                "report_date": report_date,
                "status": "failed",
                "entries_processed": entries_processed,
                "error_count": 1,
            },
        )
        IngestionRunService.finish_run(
            db,
            run,
            status="failed",
            report_date=report_date,
            entries_total=entries_processed,
            entries_processed=entries_processed,
            entries_inserted=entries_inserted,
            entries_updated=entries_updated,
            entries_skipped=entries_skipped,
            error_count=1,
            anomaly_count=0,
            anomaly_flags=[],
            error_message=e.message,
        )
        # Clean up on failure
        if pdf_path and pdf_path.exists():
            os.remove(pdf_path)
        raise  # Let Celery handle retry

    except Exception as e:
        logger.exception(
            "Unexpected error during scraping",
            extra={
                "event": "scrape_failed_unexpected",
                "task_id": self.request.id,
                "task_name": "scrape_daily_prices",
                "source_url": url,
                "source_file": pdf_path.name if pdf_path else url.split("/")[-1],
                "report_date": report_date,
                "status": "failed",
                "entries_processed": entries_processed,
                "error_count": 1,
            },
        )
        IngestionRunService.finish_run(
            db,
            run,
            status="failed",
            report_date=report_date,
            entries_total=entries_processed,
            entries_processed=entries_processed,
            entries_inserted=entries_inserted,
            entries_updated=entries_updated,
            entries_skipped=entries_skipped,
            error_count=1,
            anomaly_count=0,
            anomaly_flags=[],
            error_message=str(e),
        )
        # Clean up on failure
        if pdf_path and pdf_path.exists():
            os.remove(pdf_path)
        raise

    finally:
        db.close()
