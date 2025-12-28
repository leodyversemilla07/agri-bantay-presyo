import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.scraper.ai_processor import AIProcessor

class PriceParser:
    def __init__(self, map_path: str = None):
        if map_path is None:
            map_path = Path(__file__).parent / "map.json"
        
        with open(map_path, "r") as f:
            data = json.load(f)
            self.normalization_map = data.get("commodities", {})
        
        self.ai = AIProcessor()

    def normalize_commodity(self, name: str) -> str:
        if not name:
            return ""
        # Remove extra whitespace and newlines
        name = " ".join(name.split())
        return self.normalization_map.get(name, name)

    def is_category_row(self, row: List[Optional[str]]) -> bool:
        """
        Heuristic to identify if a row is a category header.
        Usually has data only in the first column and is in ALL CAPS.
        """
        first_col = row[0]
        if first_col and all(c is None or c == "" for c in row[1:]):
            return first_col.isupper()
        return False

    def parse_daily_prevailing(self, pdf_path: str) -> List[Dict[str, Any]]:
        results = []
        current_category = None
        
        with pdfplumber.open(pdf_path) as pdf:
            # Try to extract date from the first page
            first_page_text = pdf.pages[0].extract_text()
            report_date = self.extract_date_from_text(first_page_text)
            
            for page in pdf.pages:
                tables = page.extract_tables({
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,
                })
                
                for table in tables:
                    for row in table:
                        if not row or not any(row):
                            continue
                            
                        # Clean row
                        row = [str(cell).strip() if cell else None for cell in row]
                        
                        if self.is_category_row(row):
                            current_category = row[0]
                            continue
                        
                        # Assuming layout: Commodity | Unit | Low | High | Prevailing
                        if len(row) >= 5 and row[0] and row[4]:
                            commodity_name = row[0]
                            if commodity_name.lower() in ["commodity", "item"]:
                                continue
                                
                            try:
                                entry = {
                                    "commodity": self.normalize_commodity(commodity_name),
                                    "category": current_category,
                                    "unit": row[1],
                                    "price_low": self._parse_numeric(row[2]),
                                    "price_high": self._parse_numeric(row[3]),
                                    "price_prevailing": self._parse_numeric(row[4]),
                                    "report_date": report_date.isoformat() if report_date else None,
                                    "report_type": "DAILY_PREVAILING"
                                }
                                results.append(entry)
                            except (ValueError, TypeError):
                                continue
                                
        return results

    def parse_daily_with_ai(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Uses Gemini to extract data from the entire PDF text.
        More accurate but slower/requires API key.
        """
        raw_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text()
            report_date = self.extract_date_from_text(first_page_text)
            for page in pdf.pages:
                raw_text += page.extract_text() + "\n"

        if not self.ai.enabled:
            return self.parse_daily_prevailing(pdf_path)

        date_str = report_date.isoformat() if report_date else "unknown"
        master_list = list(set(self.normalization_map.values()))
        results = self.ai.process_messy_rows(raw_text, date_str, master_list=master_list)
        
        # Add report_date to each entry if AI missed it
        for entry in results:
            if "report_date" not in entry or not entry["report_date"]:
                entry["report_date"] = date_str
            if "report_type" not in entry:
                entry["report_type"] = "DAILY_PREVAILING"
                
        return results

    def _parse_numeric(self, value: Optional[str]) -> Optional[float]:
        if not value or value.lower() in ["n/a", "-", ""]:
            return None
        clean_val = re.sub(r'[^\d.]', '', value)
        try:
            return float(clean_val)
        except ValueError:
            return None

    def extract_date_from_text(self, text: str) -> Optional[datetime]:
        if not text:
            return None
        patterns = [
            r"([A-Z][a-z]+ \d{1,2}, \d{4})", # December 22, 2025
            r"(\d{1,2} [A-Z][a-z]+ \d{4})", # 22 December 2025
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return datetime.strptime(match.group(1), "%B %d, %Y")
                except ValueError:
                    try:
                        return datetime.strptime(match.group(1), "%d %B %Y")
                    except ValueError:
                        continue
        return None
