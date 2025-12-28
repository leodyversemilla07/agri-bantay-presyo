from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date
from typing import Optional
from decimal import Decimal
from app.schemas.commodity import Commodity
from app.schemas.market import Market

class PriceEntryBase(BaseModel):
    commodity_id: UUID
    market_id: UUID
    report_date: date
    price_low: Optional[Decimal] = None
    price_high: Optional[Decimal] = None
    price_prevailing: Optional[Decimal] = None
    price_average: Optional[Decimal] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    report_type: str
    source_file: Optional[str] = None

class PriceEntryCreate(PriceEntryBase):
    pass

class PriceEntry(PriceEntryBase):
    id: UUID
    commodity: Optional[Commodity] = None
    market: Optional[Market] = None
    
    model_config = ConfigDict(from_attributes=True)
