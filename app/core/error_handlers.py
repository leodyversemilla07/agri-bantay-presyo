"""
Global exception handlers for FastAPI application.
"""

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import (
    AgriBantayError,
    DatabaseConnectionError,
    DuplicateRecordError,
    ExternalServiceError,
    RecordNotFoundError,
    ScraperError,
    ValidationError,
)

logger = logging.getLogger(__name__)


async def agri_bantay_exception_handler(request: Request, exc: AgriBantayError):
    """Handle all custom application exceptions."""
    logger.error(f"Application error: {exc.message}", extra={"details": exc.details})

    # Map exception types to HTTP status codes
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, RecordNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DuplicateRecordError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, DatabaseConnectionError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, ExternalServiceError):
        status_code = status.HTTP_502_BAD_GATEWAY
    elif isinstance(exc, ScraperError):
        status_code = status.HTTP_502_BAD_GATEWAY

    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__,
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    logger.error(f"Database error: {str(exc)}")

    # Check for specific error types
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": True,
                "message": "Database integrity error - possibly duplicate entry",
                "type": "IntegrityError",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Database error occurred",
            "type": "DatabaseError",
        },
    )


async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")

    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "details": errors,
            "type": "ValidationError",
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    logger.exception(f"Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "An unexpected error occurred",
            "type": "InternalServerError",
        },
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    from pydantic import ValidationError as PydanticValidationError
    from sqlalchemy.exc import SQLAlchemyError

    app.add_exception_handler(AgriBantayError, agri_bantay_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
