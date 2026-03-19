import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.health import get_operational_health_status


def main() -> int:
    status = get_operational_health_status()
    if status["latest_ingestion_failure"] is not None:
        return 1
    if status["latest_ingestion_anomaly_count"] > settings.INGESTION_ALERT_MAX_ANOMALIES:
        return 1
    return 0 if status["ingestion_is_fresh"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
