import logging
from app.scraper.tasks import scrape_daily_prices
from app.scraper.source import MonitoringSource
from app.db.session import SessionLocal
from app.models.price_entry import PriceEntry
from app.models.commodity import Commodity
from app.models.market import Market
from sqlalchemy import desc, func

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_mass_ingestion():
    print(f"\n🌊 STARTING MASS DATA INGESTION")
    print("-" * 50)

    # 1. Discover latest Daily PDF links
    source = MonitoringSource()
    links = source.get_latest_pdf_links()
    daily_links = links.get("daily", [])[:3] # Start with top 3 to be safe/fast for demo
    
    if not daily_links:
        print("No daily links found!")
        return

    print(f"Discovered {len(daily_links)} latest daily reports.")
    
    for url in daily_links:
        print(f"\n📥 Ingesting: {url}")
        try:
            scrape_daily_prices(url)
            print(f"✅ Finished {url}")
        except Exception as e:
            print(f"❌ Failed {url}: {e}")

    # 2. Show Summary Table
    db = SessionLocal()
    try:
        # Get count per date
        counts = db.query(
            PriceEntry.report_date, 
            func.count(PriceEntry.id)
        ).group_by(PriceEntry.report_date).order_by(desc(PriceEntry.report_date)).all()

        print("\n📊 DATABASE SUMMARY")
        print(f"{'Report Date':<15} | {'Unique Entries'}")
        print("-" * 30)
        for d, count in counts:
            print(f"{str(d):<15} | {count}")

        # Show a sample of the actual data
        entries = db.query(PriceEntry).join(Commodity).join(Market).order_by(desc(PriceEntry.report_date), Commodity.name).limit(50).all()
        
        print("\n📝 LATEST DATA SAMPLE (Top 50)")
        print(f"{'Date':<12} | {'Commodity':<25} | {'Market':<20} | {'Price'}")
        print("-" * 85)
        for entry in entries:
            price = f"P{entry.price_prevailing:.2f}" if entry.price_prevailing else "N/A"
            print(f"{str(entry.report_date):<12} | {entry.commodity.name[:25]:<25} | {entry.market.name[:20]:<20} | {price}")
            
    finally:
        db.close()

if __name__ == "__main__":
    run_mass_ingestion()
