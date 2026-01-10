
import os
import sys
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = Path("c:/Users/Leodyver/CodeSanctum/agri-bantay-presyo/backend")
sys.path.append(str(backend_dir))

from app.scraper.tasks import scrape_daily_prices
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def ingest_sample_2025():
    test_url = "https://www.da.gov.ph/wp-content/uploads/2025/12/Price-Monitoring-December-27-2025.pdf"
    print(f"🚀 Ingesting sample 2025 data from: {test_url}")
    try:
        scrape_daily_prices(test_url)
        print("✅ Ingestion complete!")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")

if __name__ == "__main__":
    ingest_sample_2025()
