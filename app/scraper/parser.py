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
            # Try to extract date from the first two pages
            report_date = None
            for i in range(min(2, len(pdf.pages))):
                text = pdf.pages[i].extract_text()
                report_date = self.extract_date_from_text(text)
                if report_date:
                    break
            
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
                            
                        # Clean row and filter empty columns but keep positional integrity
                        cleaned_row = [str(cell).strip() if cell else None for cell in row]
                        
                        # Filter out rows that are entirely empty strings or None
                        if not any(c for c in cleaned_row if c):
                            continue

                        if self.is_category_row(cleaned_row):
                            current_category = cleaned_row[0]
                            continue
                        
                        # FILTER: Skip rows that look like markets or footnotes
                        text_content = " ".join([c for c in cleaned_row if c]).lower()
                        if any(kw in text_content for kw in ["market", "public", "agora", "cloverleaf", "plaza", "available only", "disclaimer", "source:", "note:"]):
                            continue

                        # 2025 Layout Heuristic: Detect column indices based on headers or content
                        # We look for a row that has a commodity name and at least 3 numbers
                        numeric_cells = [i for i, val in enumerate(cleaned_row) if val and self._parse_numeric(val) is not None]
                        
                        # Commodities usually start with text and don't look like footers
                        if len(cleaned_row) >= 4 and cleaned_row[0] and len(numeric_cells) >= 3:
                            commodity_name = cleaned_row[0]
                            
                            # Additional check: Commodity names shouldn't be too short or fragmented
                            if len(commodity_name) < 3 or commodity_name.lower() in ["commodity", "item", "commodities", "market"]:
                                continue
                            
                            # Extract unit from category
                            unit = "kg"
                            if current_category and "(" in current_category:
                                unit_match = re.search(r'\((.*?)\)', current_category)
                                if unit_match:
                                    unit = unit_match.group(1).replace("per ", "")

                            try:
                                # Map price indices based on detected numeric columns
                                # Usually: Low, High, Prevailing, Average
                                p_low = self._parse_numeric(cleaned_row[numeric_cells[0]])
                                p_high = self._parse_numeric(cleaned_row[numeric_cells[1]])
                                p_prev = self._parse_numeric(cleaned_row[numeric_cells[2]])
                                p_avg = self._parse_numeric(cleaned_row[numeric_cells[3]]) if len(numeric_cells) > 3 else None

                                results.append({
                                    "commodity": self.normalize_commodity(commodity_name),
                                    "category": current_category,
                                    "unit": unit,
                                    "price_low": p_low,
                                    "price_high": p_high,
                                    "price_prevailing": p_prev,
                                    "price_average": p_avg,
                                    "report_date": report_date.isoformat() if report_date else None,
                                    "report_type": "DAILY_PREVAILING"
                                })
                            except (ValueError, TypeError):
                                continue
                                
        return results

    def parse_daily_with_ai(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Uses Gemini to extract data from the entire PDF text.
        More accurate but slower/requires API key.
        """
        raw_text = ""
        report_date = None
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                raw_text += page_text + "\n"
                if not report_date:
                    report_date = self.extract_date_from_text(page_text)

        if not self.ai.enabled:
            logger.warning("AI Processor disabled, falling back to heuristic parser.")
            return self.parse_daily_prevailing(pdf_path)

        date_str = report_date.isoformat() if report_date else "unknown"
        master_list = list(set(self.normalization_map.values()))
        results = self.ai.process_messy_rows(raw_text, date_str, master_list=master_list)
        
        # Post-process AI results
        for entry in results:
            if "report_date" not in entry or not entry["report_date"] or entry["report_date"] == "unknown":
                entry["report_date"] = date_str
            if "report_type" not in entry:
                entry["report_type"] = "DAILY_PREVAILING"
            
            # Ensure numeric types
            for field in ["price_low", "price_high", "price_prevailing", "price_average"]:
                if field in entry and entry[field] is not None:
                    try:
                        entry[field] = float(entry[field])
                    except (ValueError, TypeError):
                        entry[field] = None
                
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
