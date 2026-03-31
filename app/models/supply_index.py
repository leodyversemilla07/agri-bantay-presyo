import uuid

from sqlalchemy import Column, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.types import GUID, ScaledDecimal


class SupplyIndex(Base):
    __tablename__ = "supply_indices"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    commodity_id = Column(GUID(), ForeignKey("commodities.id"), nullable=False)
    date = Column(Date, index=True, nullable=False)
    volume_metric_tons = Column(ScaledDecimal(10, 2))
    wholesale_price = Column(ScaledDecimal(10, 2))

    commodity = relationship("Commodity", back_populates="supply_indices")
