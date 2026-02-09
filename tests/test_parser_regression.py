"""
Regression tests for deterministic PDF parsing (Daily Retail Price Range).
"""

from pathlib import Path

import pytest

from app.scraper.parser import PriceParser


def _load_results(pdf_name: str):
    pdf_path = Path("downloads") / pdf_name
    if not pdf_path.exists():
        pytest.skip(f"Missing test PDF: {pdf_path}")
    parser = PriceParser()
    return parser.parse_daily_prevailing(str(pdf_path))


def _find_entry(results, market_name: str, commodity: str):
    for row in results:
        if row.get("market") == market_name and row.get("commodity") == commodity:
            return row
    return None


def test_parse_feb_9_2026_consistency():
    results = _load_results("Price-Monitoring-February-9-2026.pdf")
    assert len(results) >= 300

    entry = _find_entry(results, "Agora Public Market/San Juan", "Well-milled Rice (Local)")
    assert entry is not None
    assert entry["price_low"] == 45.0
    assert entry["price_high"] == 45.0

    egg = _find_entry(results, "Agora Public Market/San Juan", "Egg (Medium)")
    assert egg is not None
    assert egg["price_low"] == 8.5
    assert egg["price_high"] == 8.5


def test_parse_jan_20_2026_consistency():
    results = _load_results("Price-Monitoring-January-20-2026.pdf")
    assert len(results) >= 150

    entry = _find_entry(results, "Agora Public Market/San Juan", "Well-milled Rice (Local)")
    assert entry is not None
    assert entry["price_low"] == 45.0
    assert entry["price_high"] == 45.0
