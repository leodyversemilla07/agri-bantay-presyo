import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.commodity import CommodityCreate
from app.services.commodity_service import CommodityService


def seed_commodities(db: Session):
    map_path = Path(__file__).parent.parent / "scraper" / "map.json"
    with open(map_path, "r") as f:
        data = json.load(f)
        commodities = data.get("commodities", {})

    # Use unique standardized names
    unique_names = set(commodities.values())

    for name in unique_names:
        existing = CommodityService.get_by_name(db, name=name)
        if not existing:
            print(f"Seeding commodity: {name}")
            CommodityService.create(db, obj_in=CommodityCreate(name=name))


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_commodities(db)
        print("Seeding completed successfully.")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()
