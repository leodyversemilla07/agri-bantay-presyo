from app.core.config import Settings


class TestSettings:
    def test_local_defaults_use_in_memory_rate_limiting(self):
        settings = Settings(_env_file=None, APP_ENV="development", REDIS_URL="redis://localhost:6379/0")

        assert settings.RATE_LIMIT_STORAGE_URL == "memory://"

    def test_production_defaults_use_shared_runtime_settings(self):
        settings = Settings(_env_file=None, APP_ENV="production", REDIS_URL="redis://redis:6379/0")

        assert settings.RATE_LIMIT_STORAGE_URL == "redis://redis:6379/0"
        assert settings.CELERY_WORKER_POOL == "prefork"
        assert settings.CELERY_WORKER_CONCURRENCY == 2
        assert settings.CELERY_BEAT_SCHEDULE_FILE == "/app/data/celerybeat-schedule"
