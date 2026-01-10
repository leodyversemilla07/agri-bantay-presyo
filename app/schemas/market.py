from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class MarketBase(BaseModel):
    name: str
    region: Optional[str] = None
    city: Optional[str] = None
    is_regional_average: bool = False

class MarketCreate(MarketBase):
    pass

class MarketUpdate(MarketBase):
    name: Optional[str] = None

class Market(MarketBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)
