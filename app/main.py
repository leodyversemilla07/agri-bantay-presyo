import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import configure_mappers

from app.api.v1.api import api_router
from app.api.views import router as views_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers

# Configure mappers after imports
configure_mappers()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Agricultural price monitoring API for the Philippines",
    version="1.0.0",
)

# Register exception handlers
register_exception_handlers(app)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include HTML views router (must be after API router for proper routing)
app.include_router(views_router, tags=["views"])

logger.info(f"Application started: {settings.PROJECT_NAME}")
