import os
from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Agri Bantay Presyo"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    LOG_AS_JSON: bool = False
    LOG_SERVICE_NAME: str = "agri-bantay-presyo"
    BACKEND_CORS_ORIGINS: List[str] = []

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "bantay_presyo"
    DATABASE_URL: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_STORAGE_URL: Optional[str] = None
    CELERY_WORKER_POOL: Optional[str] = None
    CELERY_WORKER_CONCURRENCY: Optional[int] = None
    CELERY_BEAT_SCHEDULE_FILE: Optional[str] = None
    WAIT_FOR_SERVICES_TIMEOUT_SECONDS: int = 60
    INGESTION_STALENESS_HOURS: int = 36

    # Authentication
    API_KEY: Optional[str] = None  # Optional API key for protected endpoints
    API_KEY_HEADER: str = "X-API-Key"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100  # Max requests per window
    RATE_LIMIT_WINDOW: int = 60  # Window in seconds

    # Default market for scraper
    DEFAULT_MARKET_NAME: str = "NCR Central Market"

    # Cache TTL settings (in seconds)
    CACHE_TTL_SHORT: int = 60  # 1 minute
    CACHE_TTL_MEDIUM: int = 300  # 5 minutes
    CACHE_TTL_LONG: int = 3600  # 1 hour

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def is_windows(self) -> bool:
        return os.name == "nt"

    @model_validator(mode="after")
    def apply_runtime_defaults(self):
        if self.RATE_LIMIT_STORAGE_URL is None:
            self.RATE_LIMIT_STORAGE_URL = self.REDIS_URL if self.is_production else "memory://"

        if self.CELERY_WORKER_POOL is None:
            self.CELERY_WORKER_POOL = "prefork" if self.is_production or not self.is_windows else "solo"

        if self.CELERY_WORKER_CONCURRENCY is None:
            if self.is_production:
                self.CELERY_WORKER_CONCURRENCY = 2
            else:
                self.CELERY_WORKER_CONCURRENCY = 1 if self.is_windows else 4

        if self.CELERY_BEAT_SCHEDULE_FILE is None:
            if self.is_production:
                self.CELERY_BEAT_SCHEDULE_FILE = "/app/data/celerybeat-schedule"
            else:
                self.CELERY_BEAT_SCHEDULE_FILE = "celerybeat-schedule.local" if self.is_windows else "celerybeat-schedule"

        return self

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    @property
    def async_database_url(self) -> str:
        """Get async database URL using asyncpg driver."""
        sync_url = self.sync_database_url
        return sync_url.replace("postgresql://", "postgresql+asyncpg://")


# Create settings instance and explicitly load .env if necessary
settings = Settings()
