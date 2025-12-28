import pytest
from app.scraper.parser import PriceParser
from datetime import datetime

def test_normalize_commodity():
    parser = PriceParser()
    # Test normalization from map.json
    assert parser.normalize_commodity("Rice Special (Imp.)") == "Imported Special Rice"
    # Test unknown commodity returns same name
    assert parser.normalize_commodity("Unknown Commodity") == "Unknown Commodity"

def test_extract_date_from_text():
    parser = PriceParser()
    text = "Price Monitoring - December 22, 2025"
    extracted_date = parser.extract_date_from_text(text)
    assert extracted_date == datetime(2025, 12, 22)

    text2 = "As of 22 December 2025"
    extracted_date2 = parser.extract_date_from_text(text2)
    assert extracted_date2 == datetime(2025, 12, 22)

def test_is_category_row():
    parser = PriceParser()
    assert parser.is_category_row(["FISH", None, None, None, None]) is True
    assert parser.is_category_row(["Bangus", "kg", "100", "120", "110"]) is False
