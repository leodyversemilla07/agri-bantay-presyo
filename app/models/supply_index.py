from sqlalchemy import Column, UUID, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base

class SupplyIndex(Base):
    __tablename__ = "supply_indices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id"), nullable=False)
    date = Column(Date, index=True, nullable=False)
    volume_metric_tons = Column(Numeric(10, 2))
    wholesale_price = Column(Numeric(10, 2))

    commodity = relationship("Commodity", back_populates="supply_indices")
