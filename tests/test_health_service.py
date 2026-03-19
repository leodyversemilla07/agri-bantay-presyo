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
