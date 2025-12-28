from app.core.celery_app import celery_app
from app.scraper.downloader import PDFDownloader
from app.scraper.parser import PriceParser
from app.db.session import SessionLocal
from app.db import base
from app.services.price_service import PriceService
from app.services.commodity_service import CommodityService
from app.services.market_service import MarketService
from app.schemas.commodity import CommodityCreate
from app.schemas.market import MarketCreate
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="app.scraper.tasks.scrape_daily_prices")
def scrape_daily_prices(url: str):
    downloader = PDFDownloader()
    parser = PriceParser()
    db = SessionLocal()
    
    try:
        logger.info(f"Starting daily scrape for URL: {url}")
        pdf_path = downloader.download_pdf_sync(url)
        
        # Now using AI-powered extraction for better accuracy!
        parsed_results = parser.parse_daily_with_ai(str(pdf_path))
        
        for entry in parsed_results:
            # 1. Get or create commodity
            # Proactively normalize name using map.json
            raw_name = entry["commodity"]
            normalized_name = parser.normalization_map.get(raw_name, raw_name)
            
            commodity = CommodityService.get_or_create(
                db, 
                name=normalized_name,
                category=entry.get("category"),
                unit=entry.get("unit")
            )
            
            # 2. Get or create market (assuming a default market for now if none specified in row)
            # In actual PDFs, the market might be in the filename or header.
            # For this MVP, we'll use "Default Market" or try to extract it.
            market_name = entry.get("market", "NCR Central Market")
            market = MarketService.get_or_create(db, name=market_name)
            
            # 3. Create price entry
            PriceService.create_entry(db, {
                "commodity_id": commodity.id,
                "market_id": market.id,
                "report_date": entry["report_date"],
                "price_low": entry["price_low"],
                "price_high": entry["price_high"],
                "price_prevailing": entry["price_prevailing"],
                "report_type": entry["report_type"],
                "source_file": pdf_path.name
            })
            
        logger.info(f"Successfully processed {len(parsed_results)} entries from {pdf_path.name}")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise e
    finally:
        db.close()
