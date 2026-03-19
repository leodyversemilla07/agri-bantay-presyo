from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PriceSortField(str, Enum):
    REPORT_DATE = "report_date"
    COMMODITY_NAME = "commodity_name"
    MARKET_NAME = "market_name"
    PREVAILING_PRICE = "prevailing_price"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PriceView(str, Enum):
    FULL = "full"
    COMPACT = "compact"


class PriceFilters(BaseModel):
    report_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    commodity_id: Optional[UUID] = None
    market_id: Optional[UUID] = None
    category: Optional[str] = None
    region: Optional[str] = None
    sort_by: PriceSortField = PriceSortField.REPORT_DATE
    sort_order: SortOrder = SortOrder.DESC

    @property
    def uses_date_range(self) -> bool:
        return self.start_date is not None or self.end_date is not None
