from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Synchronous engine and session used by API handlers, Celery tasks, and scripts.
engine = create_engine(settings.sync_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Database session dependency for FastAPI handlers and scripts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
