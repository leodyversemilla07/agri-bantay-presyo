from datetime import UTC, datetime, timedelta
from pathlib import Path

import redis
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.ingestion_run_service import IngestionRunService


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_alembic_head_revision() -> str | None:
    config = Config(str(_repo_root() / "alembic.ini"))
    config.set_main_option("script_location", str(_repo_root() / "alembic"))
    return ScriptDirectory.from_config(config).get_current_head()


def get_current_schema_revision(db) -> str | None:
    table_names = inspect(db.bind).get_table_names()
    if "alembic_version" not in table_names:
        return None
    return db.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()


def get_readiness_status(db) -> dict:
    status = {
        "status": "not_ready",
        "checks": {
            "postgres": False,
            "redis": False,
            "schema_at_head": False,
        },
        "schema": {
            "current_revision": None,
            "head_revision": None,
        },
    }

    try:
        db.execute(text("SELECT 1"))
        status["checks"]["postgres"] = True
    except SQLAlchemyError:
        return status

    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        try:
            status["checks"]["redis"] = bool(redis_client.ping())
        finally:
            redis_client.close()
    except redis.RedisError:
        return status

    current_revision = get_current_schema_revision(db)
    head_revision = get_alembic_head_revision()
    status["schema"]["current_revision"] = current_revision
    status["schema"]["head_revision"] = head_revision
    status["checks"]["schema_at_head"] = bool(current_revision and head_revision and current_revision == head_revision)

    if all(status["checks"].values()):
        status["status"] = "ready"

    return status


def get_operational_health_status() -> dict:
    status = {
        "postgres": False,
        "redis": False,
        "schema_at_head": False,
        "celery_worker": False,
        "celery_beat": False,
        "latest_successful_ingestion": None,
        "latest_ingestion_failure": None,
        "ingestion_is_fresh": False,
    }

    db = SessionLocal()
    try:
        readiness = get_readiness_status(db)
        status["postgres"] = readiness["checks"]["postgres"]
        status["redis"] = readiness["checks"]["redis"]
        status["schema_at_head"] = readiness["checks"]["schema_at_head"]

        latest_run = IngestionRunService.get_latest_run(db)
        latest_success = IngestionRunService.get_latest_successful_scrape(db)
        if latest_success:
            status["latest_successful_ingestion"] = {
                "source_file": latest_success.source_file,
                "report_date": str(latest_success.report_date) if latest_success.report_date else None,
                "finished_at": latest_success.finished_at.isoformat() if latest_success.finished_at else None,
            }
            if latest_success.finished_at:
                fresh_after = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=settings.INGESTION_STALENESS_HOURS)
                status["ingestion_is_fresh"] = latest_success.finished_at >= fresh_after

        if latest_run and latest_run.status == "failed":
            status["latest_ingestion_failure"] = {
                "task_name": latest_run.task_name,
                "source_file": latest_run.source_file,
                "finished_at": latest_run.finished_at.isoformat() if latest_run.finished_at else None,
                "error_message": latest_run.error_message,
            }
    finally:
        db.close()

    try:
        status["celery_worker"] = bool(celery_app.control.ping(timeout=1.0))
    except Exception:
        status["celery_worker"] = False

    schedule_base = Path(settings.CELERY_BEAT_SCHEDULE_FILE)
    schedule_candidates = [
        schedule_base,
        Path(f"{schedule_base}.bak"),
        Path(f"{schedule_base}.dat"),
        Path(f"{schedule_base}.dir"),
    ]
    existing_schedule_files = [path for path in schedule_candidates if path.exists()]
    if existing_schedule_files:
        modified_at = max(datetime.fromtimestamp(path.stat().st_mtime) for path in existing_schedule_files)
        status["celery_beat"] = modified_at >= datetime.now() - timedelta(minutes=10)

    return status
