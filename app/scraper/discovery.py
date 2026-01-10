from app.core.celery_app import celery_app
from app.scraper.source import MonitoringSource
from app.scraper.tasks import scrape_daily_prices
from app.db.session import SessionLocal
from app.models import PriceEntry
import logging

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
    logger.info("Starting report discovery...")
    
    # Get already processed files
    processed_files = get_processed_files()
    logger.info(f"Already processed {len(processed_files)} files")
    
    # Get new PDFs only
    new_links = MonitoringSource.get_new_pdf_links(processed_files)
    
    if not new_links:
        logger.info("No new PDFs found to process")
        return {"status": "no_new_files", "processed": 0}
    
    processed_count = 0
    for url in new_links[:5]:  # Process up to 5 new PDFs at a time
        logger.info(f"Found new report: {url}, triggering scrape task.")
        try:
            scrape_daily_prices.delay(url)
            processed_count += 1
        except Exception as e:
            logger.error(f"Failed to queue {url}: {e}")
    
    return {"status": "success", "processed": processed_count, "new_files": len(new_links)}
