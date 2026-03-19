from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CountChangeMetric(BaseModel):
    count: int
    change: Optional[int] = None


class DashboardStats(BaseModel):
    latest_report_date: Optional[date] = None
    previous_report_date: Optional[date] = None
    commodities: CountChangeMetric
    markets: CountChangeMetric
    prices: CountChangeMetric


class CommodityTrendPoint(BaseModel):
    report_date: date
    prevailing_price: Optional[Decimal] = None
    market_count: int


class CommodityTrendSeries(BaseModel):
    commodity_id: UUID
    market_id: Optional[UUID] = None
    points: list[CommodityTrendPoint]


class CommodityTrendSummary(BaseModel):
    commodity_id: UUID
    market_id: Optional[UUID] = None
    latest_report_date: Optional[date] = None
    previous_report_date: Optional[date] = None
    current_prevailing_price: Optional[Decimal] = None
    previous_prevailing_price: Optional[Decimal] = None
    absolute_change: Optional[Decimal] = None
    percent_change: Optional[float] = None
    market_count: int = 0


class MarketTrendPoint(BaseModel):
    report_date: date
    prevailing_price: Optional[Decimal] = None
    commodity_count: int


class MarketTrendSeries(BaseModel):
    market_id: UUID
    commodity_id: Optional[UUID] = None
    points: list[MarketTrendPoint]


class MarketTrendSummary(BaseModel):
    market_id: UUID
    commodity_id: Optional[UUID] = None
    latest_report_date: Optional[date] = None
    previous_report_date: Optional[date] = None
    current_prevailing_price: Optional[Decimal] = None
    previous_prevailing_price: Optional[Decimal] = None
    absolute_change: Optional[Decimal] = None
    percent_change: Optional[float] = None
    commodity_count: int = 0
