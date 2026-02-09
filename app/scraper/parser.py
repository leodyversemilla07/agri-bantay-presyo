import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pdfplumber

logger = logging.getLogger(__name__)

IGNORED_KEYWORDS = (
    "market",
    "public",
    "agora",
    "cloverleaf",
    "plaza",
    "available only",
    "disclaimer",
    "source:",
    "note:",
)


@dataclass(frozen=True)
class LayoutProfile:
    name: str
    min_columns: int
    max_columns: int
    min_price: float
    max_price: float


class PriceParser:
    LAYOUT_PROFILES = [
        LayoutProfile(
            name="retail_range_2025_2026",
            min_columns=3,
            max_columns=10,
            min_price=0.5,
            max_price=10000.0,
        ),
        LayoutProfile(
            name="retail_range_generic",
            min_columns=2,
            max_columns=12,
            min_price=0.1,
            max_price=20000.0,
        ),
    ]

    def __init__(self, map_path: str = None):
        if map_path is None:
            map_path = Path(__file__).parent / "map.json"

        with open(map_path, "r") as f:
            data = json.load(f)
            self.normalization_map = data.get("commodities", {})

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
        """
        Parse Daily Retail Price Range PDFs (deterministic, layout-aware).
        """
        return self.parse_daily_retail_range(pdf_path)

    def parse_daily_retail_range(self, pdf_path: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        with pdfplumber.open(pdf_path) as pdf:
            report_date = None
            for i in range(min(2, len(pdf.pages))):
                text = pdf.pages[i].extract_text()
                report_date = self.extract_date_from_text(text)
                if report_date:
                    break

            for page in pdf.pages:
                page_text = page.extract_text() or ""
                unit = self._extract_unit_from_text(page_text) or "kg"

                words = page.extract_words()
                lines = self._group_words_by_line(words)

                header_idx = self._find_header_line_index(lines)
                if header_idx is None:
                    continue

                data_start_idx = self._find_first_data_line_index(lines, header_idx + 1)
                if data_start_idx is None:
                    continue

                header_lines = lines[header_idx:data_start_idx]
                data_lines = lines[data_start_idx:]

                col_centers = self._derive_column_centers(data_lines)
                if not col_centers:
                    continue

                market_boundary = col_centers[0] - 40
                columns = self._build_column_labels(header_lines, col_centers)
                profile = self._select_profile(columns)
                if not self._validate_column_count(columns, profile):
                    continue

                pending_market_name = ""
                for line in data_lines:
                    line_text = self._line_text(line).strip()
                    if not line_text:
                        continue

                    value_tokens = [w for w in line if self._is_value_token(w["text"])]
                    if not value_tokens and line_text:
                        pending_market_name = (pending_market_name + " " + line_text).strip()
                        continue

                    market_tokens, col_tokens = self._split_line_tokens(line, col_centers, market_boundary)
                    market_name = " ".join(market_tokens).strip()
                    if pending_market_name:
                        market_name = f"{pending_market_name} {market_name}".strip()
                        pending_market_name = ""

                    if not market_name:
                        continue

                    for col_idx, value_words in col_tokens.items():
                        commodity_name = columns.get(col_idx)
                        if not commodity_name:
                            continue

                        value_text = " ".join(value_words).strip()
                        if not value_text:
                            continue
                        if "NOT AVAILABLE" in value_text.upper():
                            continue

                        low, high = self._parse_price_range(value_text)
                        if not self._validate_price_range(low, high, profile):
                            continue
                        if low is None and high is None:
                            continue
                        prevailing = self._derive_prevailing(low, high)
                        category = self._derive_category(commodity_name)

                        results.append(
                            {
                                "commodity": self.normalize_commodity(commodity_name),
                                "category": category,
                                "unit": unit,
                                "market": market_name,
                                "price_low": low,
                                "price_high": high,
                                "price_prevailing": prevailing,
                                "price_average": None,
                                "report_date": report_date.date() if report_date else None,
                                "report_type": "DAILY_RETAIL",
                            }
                        )

        return results

    def _parse_numeric(self, value: Optional[str]) -> Optional[float]:
        if not value or value.lower() in ["n/a", "-", ""]:
            return None
        clean_val = re.sub(r"[^\d.]", "", value)
        try:
            return float(clean_val)
        except ValueError:
            return None

    def _parse_price_range(self, value: str) -> Tuple[Optional[float], Optional[float]]:
        nums = re.findall(r"\d+(?:\.\d+)?", value)
        if not nums:
            return None, None
        if len(nums) == 1:
            val = float(nums[0])
            return val, val
        low = float(nums[0])
        high = float(nums[1])
        if high < low:
            low, high = high, low
        return low, high

    def _derive_prevailing(self, low: Optional[float], high: Optional[float]) -> Optional[float]:
        if low is None and high is None:
            return None
        if low is None:
            return high
        if high is None:
            return low
        return round((low + high) / 2, 2)

    def _derive_category(self, commodity_name: str) -> Optional[str]:
        name = (commodity_name or "").lower()
        if not name:
            return None
        if "rice" in name:
            return "Rice"
        if any(k in name for k in ["egg"]):
            return "Eggs"
        if any(k in name for k in ["tilapia", "galunggong", "bangus", "sardines", "tamban", "pusit", "squid", "alumahan"]):
            return "Fish"
        if any(k in name for k in ["beef", "pork", "chicken", "kasim", "liempo", "ham", "brisket"]):
            return "Meat"
        if any(k in name for k in ["banana", "papaya", "mango", "avocado", "melon", "pomelo", "watermelon", "calamansi"]):
            return "Fruits"
        if any(k in name for k in ["onion", "garlic", "ginger", "chili", "ampalaya", "sitao", "pechay", "kalabasa", "eggplant", "tomato", "broccoli", "cabbage", "carrot", "potato", "chayote", "cauliflower", "celery", "lettuce", "bell pepper"]):
            return "Vegetables"
        if any(k in name for k in ["sugar", "oil"]):
            return "Staples"
        if any(k in name for k in ["corn", "mung bean", "mung", "grits"]):
            return "Grains"
        return None

    def extract_date_from_text(self, text: str) -> Optional[datetime]:
        if not text:
            return None
        patterns = [
            r"([A-Z][a-z]+ \d{1,2}, \d{4})",  # December 22, 2025
            r"(\d{1,2} [A-Z][a-z]+ \d{4})",  # 22 December 2025
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

    def _extract_unit_from_text(self, text: str) -> Optional[str]:
        if not text:
            return None
        match = re.search(r"COMMODITY\s*\(([^)]+)\)", text, re.IGNORECASE)
        if not match:
            return None
        unit_text = match.group(1).upper()
        if "KG" in unit_text:
            return "kg"
        if "PC" in unit_text or "PIECE" in unit_text:
            return "piece"
        if "BTL" in unit_text or "BOTTLE" in unit_text:
            return "bottle"
        return None

    def _group_words_by_line(self, words: List[Dict[str, Any]], y_tolerance: float = 3) -> List[List[Dict[str, Any]]]:
        lines: List[List[Dict[str, Any]]] = []
        for w in sorted(words, key=lambda x: (x["top"], x["x0"])):
            if not lines or abs(w["top"] - lines[-1][0]["top"]) > y_tolerance:
                lines.append([w])
            else:
                lines[-1].append(w)
        for line in lines:
            line.sort(key=lambda x: x["x0"])
        return lines

    def _find_header_line_index(self, lines: List[List[Dict[str, Any]]]) -> Optional[int]:
        for i, line in enumerate(lines):
            texts = [w["text"] for w in line]
            if not any(t.upper() == "MARKET" for t in texts):
                continue
            line_text = " ".join(texts).upper()
            if "RETAIL PRICE RANGE" in line_text:
                continue
            if line_text.startswith("NOTE"):
                continue
            if re.search(r"\b\d{4}\b", line_text):
                continue
            return i
        return None

    def _find_first_data_line_index(self, lines: List[List[Dict[str, Any]]], start: int) -> Optional[int]:
        for i in range(start, len(lines)):
            if any(self._is_value_token(w["text"]) for w in lines[i]):
                return i
        return None

    def _derive_column_centers(self, data_lines: List[List[Dict[str, Any]]]) -> List[float]:
        xs: List[float] = []
        for line in data_lines[:10]:
            for w in line:
                if self._is_value_token(w["text"]):
                    xs.append(w["x0"])
        if not xs:
            return []
        xs.sort()
        clusters: List[List[float]] = []
        threshold = 30
        for x in xs:
            if not clusters or x - clusters[-1][-1] > threshold:
                clusters.append([x])
            else:
                clusters[-1].append(x)
        centers = [sum(c) / len(c) for c in clusters]
        return centers

    def _build_column_labels(
        self, header_lines: List[List[Dict[str, Any]]], col_centers: List[float]
    ) -> Dict[int, str]:
        labels: Dict[int, List[Tuple[float, float, str]]] = {i: [] for i in range(len(col_centers))}
        for line in header_lines:
            for w in line:
                text = w["text"]
                if text.upper() == "MARKET":
                    continue
                col_idx = self._nearest_column(w["x0"], col_centers)
                if col_idx is None:
                    continue
                labels[col_idx].append((w["top"], w["x0"], text))
        final_labels: Dict[int, str] = {}
        for idx, parts in labels.items():
            parts.sort(key=lambda x: (x[0], x[1]))
            label = " ".join(p[2] for p in parts).strip()
            label = label.replace("*", "").replace("  ", " ").strip()
            final_labels[idx] = label or f"Column {idx + 1}"
        return final_labels

    def _nearest_column(self, x0: float, col_centers: List[float]) -> Optional[int]:
        if not col_centers:
            return None
        distances = [abs(x0 - c) for c in col_centers]
        return distances.index(min(distances))

    def _split_line_tokens(
        self, line: List[Dict[str, Any]], col_centers: List[float], market_boundary: float
    ) -> Tuple[List[str], Dict[int, List[str]]]:
        market_tokens: List[str] = []
        col_tokens: Dict[int, List[str]] = {i: [] for i in range(len(col_centers))}
        for w in line:
            text = w["text"]
            if w["x0"] < market_boundary:
                market_tokens.append(text)
            else:
                col_idx = self._nearest_column(w["x0"], col_centers)
                if col_idx is not None:
                    col_tokens[col_idx].append(text)
        return market_tokens, col_tokens

    def _is_value_token(self, text: str) -> bool:
        upper = text.upper()
        return bool(re.search(r"\d", text)) or upper in {"NOT", "AVAILABLE"}

    def _line_text(self, line: List[Dict[str, Any]]) -> str:
        return " ".join(w["text"] for w in line)

    def _select_profile(self, columns: Dict[int, str]) -> LayoutProfile:
        labels = " ".join(columns.values()).lower()
        if "well-milled" in labels and "egg" in labels:
            return self.LAYOUT_PROFILES[0]
        return self.LAYOUT_PROFILES[1]

    def _validate_column_count(self, columns: Dict[int, str], profile: LayoutProfile) -> bool:
        count = len([c for c in columns.values() if c])
        if count < profile.min_columns or count > profile.max_columns:
            logger.warning(
                "Skipping page: expected %s-%s columns, found %s",
                profile.min_columns,
                profile.max_columns,
                count,
            )
            return False
        return True

    def _validate_price_range(
        self, low: Optional[float], high: Optional[float], profile: LayoutProfile
    ) -> bool:
        if low is None and high is None:
            return False
        if low is None:
            low = high
        if high is None:
            high = low
        if low is None or high is None:
            return False
        if low < profile.min_price or high < profile.min_price:
            return False
        if low > profile.max_price or high > profile.max_price:
            return False
        return True
