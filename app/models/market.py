import uuid

from sqlalchemy import Boolean, Column, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.types import GUID


class Market(Base):
    __tablename__ = "markets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    region = Column(String, index=True)
    city = Column(String)
    is_regional_average = Column(Boolean, default=False)

    __table_args__ = (
        Index("uq_markets_name_ci", func.lower(name), unique=True),
    )

    price_entries = relationship("PriceEntry", back_populates="market")
