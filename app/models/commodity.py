import uuid

from sqlalchemy import Column, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.types import GUID


class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True)
    variant = Column(String)
    unit = Column(String)

    __table_args__ = (
        Index("uq_commodities_name_ci", func.lower(name), unique=True),
    )

    price_entries = relationship("PriceEntry", back_populates="commodity")
    supply_indices = relationship("SupplyIndex", back_populates="commodity")
