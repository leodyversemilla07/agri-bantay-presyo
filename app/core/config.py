import os
from typing import List, Optional

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
    BACKEND_CORS_ORIGINS: List[str] = []

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "bantay_presyo"
    DATABASE_URL: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_STORAGE_URL: str = "memory://"
    CELERY_WORKER_POOL: str = "solo" if os.name == "nt" else "prefork"
    CELERY_WORKER_CONCURRENCY: int = 1 if os.name == "nt" else 4
    CELERY_BEAT_SCHEDULE_FILE: str = "celerybeat-schedule.local" if os.name == "nt" else "celerybeat-schedule"

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
