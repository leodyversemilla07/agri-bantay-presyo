from sqlalchemy import Column, String, UUID, Boolean
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base

class Market(Base):
    __tablename__ = "markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    region = Column(String, index=True)
    city = Column(String)
    is_regional_average = Column(Boolean, default=False)

    # price_entries = relationship("PriceEntry", back_populates="market")
