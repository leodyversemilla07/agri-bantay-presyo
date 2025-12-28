from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base

class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True)
    variant = Column(String)
    unit = Column(String)

    price_entries = relationship("PriceEntry", back_populates="commodity")
    supply_indices = relationship("SupplyIndex", back_populates="commodity")
