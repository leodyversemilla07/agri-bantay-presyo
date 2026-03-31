from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import configure_mappers

from app.api.meta import router as meta_router
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.rate_limiter import limiter

# Configure mappers after imports
configure_mappers()

configure_logging()
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Agricultural price monitoring API for the Philippines",
    version="1.0.0",
)

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register exception handlers
register_exception_handlers(app)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include root metadata and versioned API routers
app.include_router(meta_router)
app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info(
    "Application started",
    extra={"event": "application_started", "status": "ok"},
)
logger.info(
    "Rate limiting configured",
    extra={"event": "rate_limit_configured"},
)
if settings.has_protected_api_keys:
    logger.info("Protected endpoint authentication is enabled", extra={"event": "api_key_enabled"})
else:
    logger.warning(
        "Protected endpoint authentication is not configured; protected routes will reject requests",
        extra={"event": "api_key_missing"},
    )
