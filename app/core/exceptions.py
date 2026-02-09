"""
Custom exception classes for Agri Bantay Presyo.
"""

from typing import Any, Dict, Optional


class AgriBantayError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# === Database Errors ===


class DatabaseError(AgriBantayError):
    """Base class for database-related errors."""

    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a requested record doesn't exist."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found",
            details={"resource": resource, "identifier": str(identifier)},
        )


class DuplicateRecordError(DatabaseError):
    """Raised when attempting to create a duplicate record."""

    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            details={"resource": resource, "field": field, "value": str(value)},
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message=message)


# === Scraper Errors ===


class ScraperError(AgriBantayError):
    """Base class for scraper-related errors."""

    pass


class PDFDownloadError(ScraperError):
    """Raised when PDF download fails."""

    def __init__(self, url: str, reason: str = "Unknown error"):
        super().__init__(
            message=f"Failed to download PDF: {reason}",
            details={"url": url, "reason": reason},
        )


class PDFParseError(ScraperError):
    """Raised when PDF parsing fails."""

    def __init__(self, filename: str, reason: str = "Unknown error"):
        super().__init__(
            message=f"Failed to parse PDF: {reason}",
            details={"filename": filename, "reason": reason},
        )


class SourceUnavailableError(ScraperError):
    """Raised when the data source is unavailable."""

    def __init__(self, source: str = "DA-AMAS", reason: str = "Connection failed"):
        super().__init__(
            message=f"Data source unavailable: {source}",
            details={"source": source, "reason": reason},
        )


# === External Service Errors ===


class ExternalServiceError(AgriBantayError):
    """Base class for external service errors."""

    pass




# === Validation Errors ===


class ValidationError(AgriBantayError):
    """Raised when data validation fails."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation error: {reason}",
            details={"field": field, "reason": reason},
        )


class InvalidDateRangeError(ValidationError):
    """Raised when date range is invalid."""

    def __init__(self, start_date: Any, end_date: Any):
        super().__init__(field="date_range", reason=f"Invalid date range: {start_date} to {end_date}")


class InvalidPriceError(ValidationError):
    """Raised when price data is invalid."""

    def __init__(self, reason: str):
        super().__init__(field="price", reason=reason)
