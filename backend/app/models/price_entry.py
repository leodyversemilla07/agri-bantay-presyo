from sqlalchemy import Column, String, UUID, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base_class import Base

class ReportType(str, enum.Enum):
    DAILY_PREVAILING = "DAILY_PREVAILING"
    WEEKLY_AVERAGE = "WEEKLY_AVERAGE"
    MARKET_DAILY_RANGE = "MARKET_DAILY_RANGE"

class PriceEntry(Base):
    __tablename__ = "price_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id"), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=False)
    report_date = Column(Date, index=True, nullable=False)
    
    # Prices
    price_low = Column(Numeric(10, 2))
    price_high = Column(Numeric(10, 2))
    price_prevailing = Column(Numeric(10, 2))
    price_average = Column(Numeric(10, 2))
    
    # Period (for weekly/monthly)
    period_start = Column(Date)
    period_end = Column(Date)
    
    report_type = Column(String, index=True) # Or use Enum(ReportType)
    source_file = Column(String)

    commodity = relationship("Commodity", back_populates="price_entries")
    market = relationship("Market")
