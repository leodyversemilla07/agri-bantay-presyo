
import os
import sys
import json
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = Path("c:/Users/Leodyver/CodeSanctum/agri-bantay-presyo/backend")
sys.path.append(str(backend_dir))

import logging
from app.scraper.parser import PriceParser
from app.scraper.downloader import PDFDownloader

def debug_heuristic():
    test_url = "https://www.da.gov.ph/wp-content/uploads/2025/12/Price-Monitoring-December-27-2025.pdf"
    
    print(f"\n🔍 DEBUGGING HEURISTIC PARSER FOR 2025")
    
    parser = PriceParser()
    downloader = PDFDownloader(download_dir=str(backend_dir / "downloads"))
    
    print("📥 Getting PDF...")
    actual_path = downloader.download_pdf_sync(test_url)
    
    import pdfplumber
    with pdfplumber.open(actual_path) as pdf:
        # Check first table on Page 5 (where summary usually is)
        page = pdf.pages[4] 
        tables = page.extract_tables({
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "snap_tolerance": 3,
        })
        
        print(f"Found {len(tables)} tables on Page 5.")
        for i, table in enumerate(tables):
            print(f"\nTable {i} Row 0-5 Raw:")
            for row in table[:5]:
                print(f"  {row}")
            
            # Simulate the parser check
            for row in table:
                if row and row[0] and "RICE" in str(row[0]).upper():
                    print(f"\nPotential Rice Row: {row}")
                    print(f"Row Length: {len(row)}")
                    break

if __name__ == "__main__":
    debug_heuristic()
