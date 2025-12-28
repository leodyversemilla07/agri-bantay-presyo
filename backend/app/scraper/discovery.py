from app.core.celery_app import celery_app
from app.scraper.source import MonitoringSource
from app.scraper.tasks import scrape_daily_prices
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="app.scraper.tasks.discover_and_scrape")
def discover_and_scrape():
    """
    Periodic task to check for new PDF reports and trigger scraping.
    """
    logger.info("Starting report discovery...")
    links = MonitoringSource.get_latest_pdf_links()
    
    # Process only the most recent daily reports for now
    # In production, we'd check if we already processed these URLs
    for url in links.get("daily", [])[:3]:
        logger.info(f"Found daily report: {url}, triggering scrape task.")
        scrape_daily_prices.delay(url)
    
    # Process latest weekly
    for url in links.get("weekly", [])[:1]:
        logger.info(f"Found weekly report: {url}")
        # scrape_weekly_prices.delay(url) # To be implemented
