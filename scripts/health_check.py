import argparse
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.health import get_operational_health_status, get_readiness_status
from app.db.session import SessionLocal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Operational and readiness health checks.")
    parser.add_argument("--mode", choices=["operational", "ready"], default="operational")
    parser.add_argument("--production", action="store_true", help="Fail on stale ingestion or latest ingestion failure.")
    parser.add_argument("--quiet", action="store_true", help="Print compact JSON without indentation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.mode == "ready":
        db = SessionLocal()
        try:
            status = get_readiness_status(db)
        finally:
            db.close()
        exit_code = 0 if status["status"] == "ready" else 1
    else:
        status = get_operational_health_status()
        exit_code = 0 if all([status["postgres"], status["redis"], status["schema_at_head"], status["celery_worker"]]) else 1
        if args.production and (
            not status["ingestion_is_fresh"]
            or status["latest_ingestion_failure"] is not None
            or status["latest_ingestion_has_anomalies"]
        ):
            exit_code = 1

    print(json.dumps(status, indent=None if args.quiet else 2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
