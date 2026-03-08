import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import configure_mappers

from app.api.meta import router as meta_router
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.core.rate_limiter import limiter

# Configure mappers after imports
configure_mappers()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

logger.info(f"Application started: {settings.PROJECT_NAME}")
logger.info(f"Rate limiting: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds")
if settings.API_KEY:
    logger.info("API key authentication is enabled")
else:
    logger.warning("API key authentication is not configured; protected write endpoints will reject requests")
