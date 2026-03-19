from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.health import get_readiness_status
from app.db.session import get_db

router = APIRouter()


@router.get("/", tags=["meta"])
def read_root():
    """Return API metadata at the service root."""
    return {
        "name": settings.PROJECT_NAME,
        "type": "rest-api",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": f"{settings.API_V1_STR}/openapi.json",
        "api_base_url": settings.API_V1_STR,
    }


@router.get("/health", tags=["meta"])
def health_check():
    """Lightweight health endpoint for uptime checks."""
    return {"status": "ok"}


@router.get("/health/ready", tags=["meta"])
def readiness_check(response: Response, db: Session = Depends(get_db)):
    """Readiness endpoint for DB, Redis, and migration-state checks."""
    readiness = get_readiness_status(db)
    if readiness["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return readiness
