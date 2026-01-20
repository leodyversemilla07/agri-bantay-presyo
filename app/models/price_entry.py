import uuid

from sqlalchemy import UUID, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PriceEntry(Base):
    __tablename__ = "price_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id"), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=False)
    report_date = Column(Date, index=True, nullable=False)

    price_low = Column(Numeric(10, 2))
    price_high = Column(Numeric(10, 2))
    price_prevailing = Column(Numeric(10, 2))
    price_average = Column(Numeric(10, 2))

    report_type = Column(String, index=True, default="DAILY_RETAIL")
    source_file = Column(String)

    commodity = relationship("Commodity", back_populates="price_entries")
    market = relationship("Market")
