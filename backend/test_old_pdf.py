import asyncio
import logging
from app.scraper.tasks import scrape_daily_prices
from app.db.session import SessionLocal
from app.services.price_service import PriceService
from app.models.price_entry import PriceEntry
from sqlalchemy import desc

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_oldest_ingestion():
    # Oldest identified PDF
    url = "http://www.da.gov.ph/wp-content/uploads/2018/02/Price-Watch-February-1-2018.pdf"
    
    logger.info(f"Triggering scrape for oldest report: {url}")
    
    # We call the task function directly (assuming it can run synchronously or we handle the async parts inside if needed)
    # The task `scrape_daily_prices` is a Celery task, but the logic inside calls async functions.
    # However, `scrape_daily_prices` itself is synchronous wrapper? Let's check tasks.py content first.
    # Actually, let's just use the logic from within the task or call the task if we have a worker running?
    # Better to replicate the logic here to see output immediately.
    
    from app.scraper.downloader import PDFDownloader
    from app.scraper.parser import PriceParser
    from app.scraper.ai_processor import AIProcessor
    
    try:
        # Download
        downloader = PDFDownloader()
        pdf_path = await downloader.download_pdf_async(url)
        if not pdf_path:
            logger.error("Failed to download PDF")
            return

        logger.info(f"Downloaded to {pdf_path}")
        
        # Parse with AI
        parser = PriceParser()
        # Note: 2018 PDFs might be image-based or have different text layout.
        # AI Processor should handle "messy text" if extractable.
        
        prices = parser.parse_daily_with_ai(pdf_path) # Extracted internally
        
        if not prices:
             logger.warning("No prices extracted.")
        else:
             logger.info(f"Successfully extracted {len(prices)} prices.")
             for p in prices[:5]:
                 logger.info(f"Sample: {p}")

             from app.services.commodity_service import CommodityService
             from app.services.market_service import MarketService
             
             # Save to DB
             db = SessionLocal()
             try:
                 for entry in prices:
                     # Resolve Commodity ID
                     commodity_name = entry.get("commodity")
                     if not commodity_name: continue
                     
                     commodity_obj = CommodityService.get_or_create(db, commodity_name, category=entry.get("category", "Other"))
                     
                     # Resolve Market ID
                     market_name = entry.get("market", "Metro Manila")
                     market_obj = MarketService.get_or_create(db, market_name)

                     # Prepare data for PriceEntry
                     db_data = {
                         "commodity_id": commodity_obj.id,
                         "market_id": market_obj.id,
                         "report_date": entry.get("report_date"),
                         "price_prevailing": entry.get("price_prevailing"),
                         "price_low": entry.get("price_low"),
                         "price_high": entry.get("price_high"),
                         "report_type": entry.get("report_type", "DAILY_PREVAILING")
                     }
                     
                     PriceService.create_entry(db, db_data)
                 db.commit()
                 logger.info("Saved to database.")
             except Exception as e:
                 logger.error(f"DB Error: {e}")
             finally:
                 db.close()

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_oldest_ingestion())
