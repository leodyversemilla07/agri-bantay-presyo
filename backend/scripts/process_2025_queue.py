
import os
import sys
import json
import time
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.scraper.tasks import scrape_daily_prices
from app.db.session import SessionLocal
from app.models.price_entry import PriceEntry
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(backend_dir / "ingestion_2025.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

QUEUE_FILE = backend_dir / "data" / "filtered_da_retail_prices.json"

def process_queue():
    if not QUEUE_FILE.exists():
        logger.error(f"Queue file not found: {QUEUE_FILE}. Run fetch_all_links.py first.")
        return

    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)

    logger.info(f"🚀 Starting ingestion of {len(queue)} reports for 2025.")
    
    db = SessionLocal()
    
    # Get list of already processed files to avoid re-downloading/parsing if possible
    processed_files = set(row[0] for row in db.query(PriceEntry.source_file).distinct().all())
    db.close()

    success_count = 0
    fail_count = 0
    
    for i, entry in enumerate(queue):
        url = entry["url"]
        filename = url.split("/")[-1]
        
        if filename in processed_files:
            logger.info(f"⏩ [{i+1}/{len(queue)}] Skipping already processed: {filename}")
            continue

        logger.info(f"📥 [{i+1}/{len(queue)}] Processing: {filename} ({entry['date']})")
        
        try:
            # We call the task logic directly here for the script
            # In a real production setup, we might use .delay() if Celery is running
            scrape_daily_prices(url)
            success_count += 1
            logger.info(f"✅ Successfully ingested {filename}")
            
            # small delay to be nice to the DA server and Gemini API rate limits
            time.sleep(1) 
            
        except Exception as e:
            fail_count += 1
            logger.error(f"❌ Failed to process {filename}: {e}")
            # Keep going with the rest of the queue
            continue

    logger.info("-" * 50)
    logger.info(f"🏁 INGESTION COMPLETE")
    logger.info(f"Total: {len(queue)}")
    logger.info(f"Success: {success_count}")
    logger.info(f"Failed: {fail_count}")
    logger.info("-" * 50)

if __name__ == "__main__":
    process_queue()
