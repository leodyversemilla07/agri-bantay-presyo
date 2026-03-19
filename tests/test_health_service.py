from types import SimpleNamespace

from app.core import health


class DummyRedisClient:
    def ping(self):
        return True

    def close(self):
        pass


def test_get_readiness_status_reports_ready(monkeypatch, db_session):
    monkeypatch.setattr(health.redis.Redis, "from_url", lambda url: DummyRedisClient())
    monkeypatch.setattr(health, "get_current_schema_revision", lambda db: "head")
    monkeypatch.setattr(health, "get_alembic_head_revision", lambda: "head")

    status = health.get_readiness_status(db_session)

    assert status["status"] == "ready"
    assert status["checks"] == {"postgres": True, "redis": True, "schema_at_head": True}


def test_get_readiness_status_reports_not_ready_on_schema_mismatch(monkeypatch, db_session):
    monkeypatch.setattr(health.redis.Redis, "from_url", lambda url: DummyRedisClient())
    monkeypatch.setattr(health, "get_current_schema_revision", lambda db: "old")
    monkeypatch.setattr(health, "get_alembic_head_revision", lambda: "head")

    status = health.get_readiness_status(db_session)

    assert status["status"] == "not_ready"
    assert status["checks"]["postgres"] is True
    assert status["checks"]["redis"] is True
    assert status["checks"]["schema_at_head"] is False


def test_get_operational_health_reports_ingestion_anomalies(monkeypatch):
    monkeypatch.setattr(
        health,
        "SessionLocal",
        lambda: SimpleNamespace(close=lambda: None),
    )
    monkeypatch.setattr(
        health,
        "get_readiness_status",
        lambda db: {"checks": {"postgres": True, "redis": True, "schema_at_head": True}},
    )
    monkeypatch.setattr(
        health.IngestionRunService,
        "get_latest_run",
        lambda db: None,
    )
    monkeypatch.setattr(
        health.IngestionRunService,
        "get_latest_successful_scrape",
        lambda db: SimpleNamespace(
            source_file="sample.pdf",
            report_date=None,
            finished_at=None,
            entries_total=10,
            entries_processed=10,
            entries_inserted=8,
            entries_updated=1,
            entries_skipped=1,
            anomaly_count=2,
            anomaly_flags=["duplicate_entries_in_source:1", "high_missing_prevailing_ratio:4/10"],
        ),
    )
    monkeypatch.setattr(health.celery_app.control, "ping", lambda timeout=1.0: [{"worker": "pong"}])
    monkeypatch.setattr(health.Path, "exists", lambda self: False)

    status = health.get_operational_health_status()

    assert status["latest_ingestion_has_anomalies"] is True
    assert status["latest_ingestion_anomaly_count"] == 2
    assert status["latest_ingestion_anomaly_flags"] == [
        "duplicate_entries_in_source:1",
        "high_missing_prevailing_ratio:4/10",
    ]
