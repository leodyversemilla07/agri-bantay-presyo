from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.commodity import Commodity
from app.schemas.commodity import CommodityCreate, CommodityUpdate

class CommodityService:
    @staticmethod
    def get(db: Session, commodity_id: str) -> Optional[Commodity]:
        return db.query(Commodity).filter(Commodity.id == commodity_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Commodity]:
        return db.query(Commodity).filter(Commodity.name == name).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> List[Commodity]:
        query = db.query(Commodity)
        if category:
            query = query.filter(Commodity.category == category)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, obj_in: CommodityCreate) -> Commodity:
        db_obj = Commodity(
            name=obj_in.name,
            category=obj_in.category,
            variant=obj_in.variant,
            unit=obj_in.unit
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_or_create(db: Session, name: str, **kwargs) -> Commodity:
        import json
        from pathlib import Path
        
        # Load map to normalize name before lookup
        map_path = Path(__file__).parent.parent / "scraper" / "map.json"
        normalized_name = name
        if map_path.exists():
            with open(map_path, "r") as f:
                mapping = json.load(f).get("commodities", {})
                normalized_name = mapping.get(name, name)
        
        commodity = CommodityService.get_by_name(db, normalized_name)
        if not commodity:
            db_obj = Commodity(name=normalized_name, **kwargs)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        return commodity
