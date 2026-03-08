from fastapi import APIRouter

from app.core.config import settings

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
