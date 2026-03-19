import uuid

from sqlalchemy import Column, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.types import GUID


class PriceEntry(Base):
    __tablename__ = "price_entries"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    commodity_id = Column(GUID(), ForeignKey("commodities.id"), nullable=False)
    market_id = Column(GUID(), ForeignKey("markets.id"), nullable=False)
    report_date = Column(Date, index=True, nullable=False)

    price_low = Column(Numeric(10, 2))
    price_high = Column(Numeric(10, 2))
    price_prevailing = Column(Numeric(10, 2))
    price_average = Column(Numeric(10, 2))
    period_start = Column(Date)
    period_end = Column(Date)

    report_type = Column(String, index=True, default="DAILY_RETAIL")
    source_file = Column(String)

    __table_args__ = (
        UniqueConstraint(
            "commodity_id",
            "market_id",
            "report_date",
            "report_type",
            name="uq_price_entries_identity",
        ),
    )

    commodity = relationship("Commodity", back_populates="price_entries")
    market = relationship("Market")
