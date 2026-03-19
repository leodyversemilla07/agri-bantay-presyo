import json
import logging
from datetime import UTC, datetime

from app.core.config import settings


class JsonLogFormatter(logging.Formatter):
    """Emit structured JSON logs that work well in container environments."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": settings.LOG_SERVICE_NAME,
            "environment": settings.APP_ENV,
            "message": record.getMessage(),
        }

        for field in (
            "event",
            "task_id",
            "task_name",
            "source_url",
            "source_file",
            "report_date",
            "status",
            "entries_total",
            "entries_processed",
            "error_count",
            "elapsed_seconds",
            "schema_at_head",
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure root logging once for API, scripts, and Celery processes."""
    root_logger = logging.getLogger()
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    formatter: logging.Formatter

    if settings.LOG_AS_JSON or settings.is_production:
        formatter = JsonLogFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
