import io
import sys
from pathlib import Path

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add the backend directory to sys.path so we can import app
backend_dir = Path("c:/Users/Leodyver/CodeSanctum/agri-bantay-presyo/backend")
sys.path.append(str(backend_dir))

import logging

from app.db.session import SessionLocal
from app.scraper.downloader import PDFDownloader
from app.scraper.parser import PriceParser

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_2025_alignment():
    # Use the December 27, 2025 report we found earlier
    test_url = "https://www.da.gov.ph/wp-content/uploads/2025/12/Price-Monitoring-December-27-2025.pdf"

    print("\n🚀 TESTING 2025 ALIGNMENT")
    print(f"Target URL: {test_url}")
    print("-" * 50)

    db = SessionLocal()

    try:
        parser = PriceParser()
        downloader = PDFDownloader(download_dir=str(backend_dir / "downloads"))

        print("\n📥 Downloading PDF...")
        actual_path = downloader.download_pdf_sync(test_url)
        print(f"Downloaded to: {actual_path}")

        # 1. Test AI Parser with new fields
        print("\n🤖 Calling AI Parser (Checking price_average and Units)...")
        ai_results = parser.parse_daily_with_ai(str(actual_path))

        if ai_results:
            sample = ai_results[0]
            print(f"✅ AI returned {len(ai_results)} rows.")
            print(f"Sample Row: {sample}")

            # Check for new fields
            has_average = any("price_average" in row and row["price_average"] is not None for row in ai_results)
            print(f"{'✅' if has_average else '❌'} price_average detected in AI results")

            has_units = any("unit" in row and row["unit"] and row["unit"] != "N/A" for row in ai_results)
            print(f"{'✅' if has_units else '❌'} Units detected in AI results")
        else:
            print("❌ AI returned no results. Check GEMINI_API_KEY.")

        # 2. Test Heuristic Parser for 2025 Layout
        print("\n🧩 Calling Heuristic Parser (Checking 2025 Column Mapping)...")
        heuristic_results = parser.parse_daily_prevailing(str(actual_path))

        if heuristic_results:
            sample = heuristic_results[0]
            print(f"✅ Heuristic returned {len(heuristic_results)} rows.")
            print(f"Sample Row: {sample}")

            # Check if columns are shifted (Low should be a number, not text or unit)
            if isinstance(sample.get("price_low"), (int, float)):
                print("✅ Price Low is numeric (Columns NOT shifted)")
            else:
                print(f"❌ Price Low is {type(sample.get('price_low'))} (Columns may still be shifted)")
        else:
            print("❌ Heuristic returned no results.")

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_2025_alignment()
