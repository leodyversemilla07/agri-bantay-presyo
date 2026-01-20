import logging

from app.db.session import SessionLocal
from app.models.commodity import Commodity
from app.models.price_entry import PriceEntry
from app.scraper.tasks import scrape_daily_prices

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ai_extraction():
    test_url = "https://www.da.gov.ph/wp-content/uploads/2025/12/December-28-2025-DPI-AFC.pdf"

    print("\n🚀 STARTING AI-POWERED EXTRACTION TEST")
    print(f"Target URL: {test_url}")
    print("-" * 50)

    db = SessionLocal()
    # Clear existing entries for this specific date to verify fresh extraction
    # (Optional, but good for testing)

    try:
        from app.scraper.parser import PriceParser

        parser = PriceParser()

        # Download manually for debugging
        from app.scraper.downloader import PDFDownloader

        downloader = PDFDownloader()
        actual_path = downloader.download_pdf_sync(test_url)

        print("\n🤖 Calling AI Parser...")
        results = parser.parse_daily_with_ai(str(actual_path))
        print(f"AI returned {len(results)} structured rows.")

        if results:
            print(f"First row from AI: {results[0]}")

        # Now run the task logic
        scrape_daily_prices(test_url)

        # Verify results
        entries = db.query(PriceEntry).join(Commodity).order_by(Commodity.name).all()

        print("\n✅ AI Extraction Successful!")
        print(f"Total entries now in DB: {len(entries)}")

        print("\n--- Sample AI-Parsed Data ---")
        print(f"{'Commodity':<30} | {'Category':<15} | {'Prevailing'}")
        print("-" * 60)

        # Show top 15 results
        for entry in entries[:15]:
            price = f"P{entry.price_prevailing:.2f}" if entry.price_prevailing else "N/A"
            print(f"{entry.commodity.name[:30]:<30} | {entry.commodity.category or 'N/A':<15} | {price}")

    except Exception as e:
        print(f"❌ AI Extraction Failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_ai_extraction()
