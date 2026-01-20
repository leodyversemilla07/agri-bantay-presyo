from typing import List

from pydantic import BaseModel


class CommodityDefinition(BaseModel):
    name: str  # The detected name in the PDF header (flattened)
    db_name: str  # The canonical name in the DB
    category: str
    unit: str = "kg"


class PDFPageConfig(BaseModel):
    page_index: int  # 0-based
    header_rows: List[int] = [0, 1]  # Rows to be merged for commodity headers
    market_col_index: int = 0

    # Known column mapping if fixed, otherwise parsers should detect dynamic
    # For now, we rely on dynamic header detection, but this config serves as the "Schema"


class ParsingProfile(BaseModel):
    name: str = "DA_Retail_Price_2025"
    year_scope: int = 2025

    # Keywords to identify detection
    header_keywords: List[str] = ["COMMODITY", "MARKET", "RICE", "FISH", "VEGETABLES"]

    # Regex for price validation
    price_regex: str = r"([\d,]+\.?\d*)\s*-?\s*([\d,]+\.?\d*)?"

    # Expected Categories to help header merging
    expected_categories: List[str] = [
        "IMPORTED COMMERCIAL RICE",
        "LOCAL COMMERCIAL RICE",
        "FISH",
        "LIVESTOCK",
        "POULTRY",
        "VEGETABLES",
        "FRUITS",
        "SPICES",
        "OTHER COMMODITIES",
    ]


# Default profile instance
PROFILE_2025 = ParsingProfile()
