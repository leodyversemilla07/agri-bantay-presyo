from app.core.celery_app import celery_app
from app.scraper.source import MonitoringSource
from app.scraper.tasks import scrape_daily_prices
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.scraper.tasks.discover_and_scrape")
def discover_and_scrape():
    """
    Periodic task to check for new Daily Retail Price PDFs and trigger scraping.
    """
    logger.info("Starting report discovery...")
    links = MonitoringSource.get_latest_pdf_links()

    for url in links[:3]:
        logger.info(f"Found daily report: {url}, triggering scrape task.")
        scrape_daily_prices.delay(url)
