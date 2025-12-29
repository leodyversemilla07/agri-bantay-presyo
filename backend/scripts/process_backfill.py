import asyncio
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys

# Add parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper.downloader import PDFDownloader
from app.scraper.parser import PriceParser

# Fix model initialization: Register all models first
from app.db import base
from sqlalchemy.orm import configure_mappers
configure_mappers()

from app.models import Commodity, Market, PriceEntry, SupplyIndex
from app.services.price_service import PriceService
from app.services.commodity_service import CommodityService
from app.services.market_service import MarketService
from app.db.session import SessionLocal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backfill.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

QUEUE_FILE = os.path.join("data", "filtered_da_retail_prices.json")
PROCESSED_FILE = os.path.join("data", "processed_files.json")

def load_processed() -> List[str]:
    if Path(PROCESSED_FILE).exists():
        with open(PROCESSED_FILE, "r") as f:
            return json.load(f)
    return []

def save_processed(processed: List[str]):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(processed, f, indent=2)

async def process_file(entry: Dict, db):
    url = entry['url']
    date_str = entry['date']
    
    logger.info(f"Processing: {date_str} - {url}")
    
    try:
        # Download
        downloader = PDFDownloader()
        pdf_path = await downloader.download_pdf_async(url)
        
        # Parse
        parser = PriceParser()
        # Use simple parsing if possible to save AI tokens, but AI is best for robust extraction
        # We will use AI for now as requested for "oldest data" which is messy
        prices = parser.parse_daily_with_ai(pdf_path)
        
        if not prices:
            logger.warning(f"No prices found in {pdf_path}")
            return
            
        logger.info(f"Extracted {len(prices)} prices.")
        
        # Save to DB
        for p in prices:
            # Normalize Commodity
            c_name = p.get("commodity")
            if not c_name: continue
            
            # Simple category fallback
            cat = p.get("category", "Other")
            
            # Get/Create Commodity
            # Using synchronous calls here; effectively blocking but fine for script
            # Note: create_entry does a lot of this, but we need IDs first
            
            # We need to use the Services appropriately
            # Since we are inside async function but services use sync DB session
            # We can just call them directly as the DB session is passed in
            
            com = CommodityService.get_or_create(db, c_name, category=cat)
            mkt = MarketService.get_or_create(db, p.get("market", "Metro Manila"))
            
            data = {
                "commodity_id": com.id,
                "market_id": mkt.id,
                "report_date": p.get("report_date") or date_str, # Fallback to filename date
                "price_prevailing": p.get("price_prevailing"),
                "price_low": p.get("price_low"),
                "price_high": p.get("price_high"),
                "report_type": "DAILY_PREVAILING"
            }
            
            PriceService.create_entry(db, data)
            
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Failed to process {url}: {e}")
        return False

async def main():
    if not Path(QUEUE_FILE).exists():
        logger.error("Queue file not found. Run fetch_all_links.py first.")
        return

    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)
        
    processed = load_processed()
    processed_urls = set(processed)
    
    # Queue is already sorted Oldest -> Newest by fetch_all_links.py
    # queue.reverse() 
    
    db = SessionLocal()
    
    try:
        count = 0
        limit = 2000 # Set to high number to process all links
        
        for entry in queue:
            if count >= limit:
                break
                
            if entry['url'] in processed_urls:
                continue
                
            success = await process_file(entry, db)
            
            if success:
                processed.append(entry['url'])
                save_processed(processed)
                count += 1
                
            # Rate limit mainly for Gemini/PDF download
            await asyncio.sleep(2) 
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
