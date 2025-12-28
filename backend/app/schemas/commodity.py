from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class CommodityBase(BaseModel):
    name: str
    category: Optional[str] = None
    variant: Optional[str] = None
    unit: Optional[str] = None

class CommodityCreate(CommodityBase):
    pass

class CommodityUpdate(CommodityBase):
    name: Optional[str] = None

class Commodity(CommodityBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)
