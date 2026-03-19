import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.data_integrity_service import DataIntegrityService


def main() -> int:
    db = SessionLocal()
    try:
        report = DataIntegrityService.generate_duplicate_report(db)
        summary = {
            "commodity_duplicates": len(report["commodity_duplicates"]),
            "market_duplicates": len(report["market_duplicates"]),
            "price_entry_duplicates": len(report["price_entry_duplicates"]),
        }
        print(json.dumps(summary, indent=2, default=str))
        return 1 if any(summary.values()) else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
