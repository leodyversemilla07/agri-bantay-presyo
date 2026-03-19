import logging
import time

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import PriceEntry
from app.scraper.source import MonitoringSource
from app.scraper.tasks import scrape_daily_prices
from app.services.ingestion_run_service import IngestionRunService

logger = logging.getLogger(__name__)


def get_processed_files() -> list:
    """Get list of already processed source files from database."""
    db = SessionLocal()
    try:
        files = db.query(PriceEntry.source_file).distinct().all()
        return [f[0] for f in files if f[0]]
    finally:
        db.close()


@celery_app.task(name="app.scraper.tasks.discover_and_scrape")
def discover_and_scrape():
    """
    Periodic task to check for new Daily Retail Price PDFs and trigger scraping.
    Only processes PDFs that haven't been ingested yet.
    """
    started_at = time.monotonic()
    logger.info(
        "Starting report discovery",
        extra={"event": "discovery_started", "task_name": "discover_and_scrape"},
    )
    db = SessionLocal()
    run = IngestionRunService.start_run(db, task_name="discover_and_scrape")

    try:
        # Get already processed files
        processed_files = get_processed_files()
        logger.info(
            "Loaded processed source file inventory",
            extra={
                "event": "discovery_loaded_processed_files",
                "task_name": "discover_and_scrape",
                "entries_processed": len(processed_files),
            },
        )

        # Get new PDFs only
        new_links = MonitoringSource.get_new_pdf_links(processed_files)

        if not new_links:
            logger.info(
                "No new PDFs found to process",
                extra={"event": "discovery_no_new_files", "task_name": "discover_and_scrape", "status": "no_new_files"},
            )
            IngestionRunService.finish_run(
                db,
                run,
                status="no_new_files",
                entries_total=0,
                entries_processed=0,
                error_count=0,
            )
            return {"status": "no_new_files", "processed": 0}

        processed_count = 0
        queue_errors = 0
        for url in new_links[:5]:  # Process up to 5 new PDFs at a time
            logger.info(
                "Queueing scrape task for new report",
                extra={
                    "event": "discovery_queueing_scrape",
                    "task_name": "discover_and_scrape",
                    "source_url": url,
                    "source_file": url.split("/")[-1],
                },
            )
            try:
                scrape_daily_prices.delay(url)
                processed_count += 1
            except Exception:
                queue_errors += 1
                logger.error(
                    "Failed to queue scrape task",
                    extra={
                        "event": "discovery_queue_failed",
                        "task_name": "discover_and_scrape",
                        "source_url": url,
                        "source_file": url.split("/")[-1],
                        "error_count": queue_errors,
                    },
                )

        status = "success" if queue_errors == 0 else "partial_success"
        IngestionRunService.finish_run(
            db,
            run,
            status=status,
            entries_total=len(new_links),
            entries_processed=processed_count,
            error_count=queue_errors,
            error_message=None if queue_errors == 0 else "One or more scrape tasks failed to queue",
        )
        logger.info(
            "Report discovery completed",
            extra={
                "event": "discovery_completed",
                "task_name": "discover_and_scrape",
                "status": status,
                "entries_total": len(new_links),
                "entries_processed": processed_count,
                "error_count": queue_errors,
                "elapsed_seconds": round(time.monotonic() - started_at, 3),
            },
        )

        return {
            "status": status,
            "processed": processed_count,
            "new_files": len(new_links),
        }
    except Exception as exc:
        IngestionRunService.finish_run(
            db,
            run,
            status="failed",
            entries_total=0,
            entries_processed=0,
            error_count=1,
            error_message=str(exc),
        )
        logger.exception(
            "Report discovery failed",
            extra={"event": "discovery_failed", "task_name": "discover_and_scrape", "status": "failed", "error_count": 1},
        )
        raise
    finally:
        db.close()
