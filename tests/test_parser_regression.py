"""
Regression tests for deterministic PDF parsing (Daily Retail Price Range).
"""

import json
from pathlib import Path
from unittest.mock import patch

from app.scraper.parser import PriceParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class _MockPage:
    def __init__(self, text, words):
        self._text = text
        self._words = words

    def extract_text(self):
        return self._text

    def extract_words(self):
        return self._words


class _MockPDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _load_results(snapshot_name: str):
    fixture_path = FIXTURES_DIR / snapshot_name
    assert fixture_path.exists(), f"Missing parser regression fixture: {fixture_path}"

    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    pages = [_MockPage(page["text"], page["words"]) for page in payload["pages"]]
    parser = PriceParser()

    with patch("app.scraper.parser.pdfplumber.open", return_value=_MockPDF(pages)):
        return parser.parse_daily_prevailing("fixture.pdf")


def _find_entry(results, market_name: str, commodity: str):
    for row in results:
        if row.get("market") == market_name and row.get("commodity") == commodity:
            return row
    return None


def test_parse_dec_27_2025_consistency():
    results = _load_results("Price-Monitoring-December-27-2025.json")
    assert len(results) >= 80

    entry = _find_entry(results, "Agora Public Market/San Juan", "Well-milled Rice (Local)")
    assert entry is not None
    assert entry["price_low"] == 45.0
    assert entry["price_high"] == 45.0
    assert str(entry["report_date"]) == "2025-12-27"

    egg = _find_entry(results, "Agora Public Market/San Juan", "Egg (Medium)")
    assert egg is not None
    assert egg["price_low"] == 8.5
    assert egg["price_high"] == 8.5


def test_parse_jan_20_2026_consistency():
    results = _load_results("Price-Monitoring-January-20-2026.json")
    assert len(results) >= 90

    entry = _find_entry(results, "Agora Public Market/San Juan", "Well-milled Rice (Local)")
    assert entry is not None
    assert entry["price_low"] == 45.0
    assert entry["price_high"] == 45.0
    assert str(entry["report_date"]) == "2026-01-20"

    egg = _find_entry(results, "Agora Public Market/San Juan", "Egg (Medium)")
    assert egg is not None
    assert egg["price_low"] == 8.5
    assert egg["price_high"] == 8.5
