"""
Tests for error handling and exceptions.
"""

from unittest.mock import patch

import pytest

from app.core.exceptions import (
    AgriBantayError,
    AIConfigurationError,
    AIProcessingError,
    AIRateLimitError,
    DuplicateRecordError,
    InvalidDateRangeError,
    PDFDownloadError,
    PDFParseError,
    RecordNotFoundError,
    ValidationError,
)


class TestCustomExceptions:
    """Tests for custom exception classes."""

    def test_agri_bantay_error_basic(self):
        """Test base exception."""
        exc = AgriBantayError("Test error")
        assert exc.message == "Test error"
        assert exc.details == {}
        assert str(exc) == "Test error"

    def test_agri_bantay_error_with_details(self):
        """Test exception with details."""
        exc = AgriBantayError("Error", details={"key": "value"})
        assert exc.details == {"key": "value"}

    def test_record_not_found_error(self):
        """Test RecordNotFoundError."""
        exc = RecordNotFoundError("Commodity", "abc-123")
        assert exc.message == "Commodity not found"
        assert exc.details["resource"] == "Commodity"
        assert exc.details["identifier"] == "abc-123"

    def test_duplicate_record_error(self):
        """Test DuplicateRecordError."""
        exc = DuplicateRecordError("Commodity", "name", "Rice")
        assert "already exists" in exc.message
        assert exc.details["field"] == "name"
        assert exc.details["value"] == "Rice"

    def test_pdf_download_error(self):
        """Test PDFDownloadError."""
        exc = PDFDownloadError(url="http://example.com/file.pdf", reason="Timeout")
        assert "download" in exc.message.lower()
        assert exc.details["url"] == "http://example.com/file.pdf"
        assert exc.details["reason"] == "Timeout"

    def test_pdf_parse_error(self):
        """Test PDFParseError."""
        exc = PDFParseError(filename="test.pdf", reason="Invalid format")
        assert "parse" in exc.message.lower()
        assert exc.details["filename"] == "test.pdf"

    def test_ai_processing_error(self):
        """Test AIProcessingError."""
        exc = AIProcessingError(service="Gemini", reason="API error")
        assert "Gemini" in exc.details["service"]
        assert exc.details["reason"] == "API error"

    def test_ai_rate_limit_error(self):
        """Test AIRateLimitError."""
        exc = AIRateLimitError(retry_after=60)
        assert "rate limit" in exc.message.lower()
        assert exc.details["retry_after_seconds"] == 60

    def test_ai_configuration_error(self):
        """Test AIConfigurationError."""
        exc = AIConfigurationError(reason="API key missing")
        assert "configuration" in exc.message.lower()

    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError(field="price", reason="Must be positive")
        assert exc.details["field"] == "price"
        assert exc.details["reason"] == "Must be positive"

    def test_invalid_date_range_error(self):
        """Test InvalidDateRangeError."""
        from datetime import date

        exc = InvalidDateRangeError(date(2025, 1, 20), date(2025, 1, 10))
        assert exc.details["field"] == "date_range"


class TestExceptionHandlers:
    """Tests for exception handlers."""

    def test_record_not_found_returns_404(self, client):
        """Test that RecordNotFoundError returns 404."""
        # Try to get a non-existent commodity
        response = client.get("/api/v1/commodities/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_create_duplicate_returns_400(self, client, sample_commodity):
        """Test that duplicate creation returns error."""
        response = client.post("/api/v1/commodities/", json={"name": sample_commodity.name, "category": "Test"})
        assert response.status_code == 400

    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoint returns 404."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404


class TestDownloaderErrorHandling:
    """Tests for PDFDownloader error handling."""

    def test_download_timeout_raises_error(self):
        """Test that timeout raises PDFDownloadError."""
        from app.scraper.downloader import PDFDownloader

        downloader = PDFDownloader()
        downloader.MAX_RETRIES = 1  # Reduce retries for test
        downloader.TIMEOUT = 0.1  # Very short timeout

        with pytest.raises(PDFDownloadError) as exc_info:
            downloader.download_pdf_sync("http://10.255.255.1/nonexistent.pdf")

        assert "nonexistent.pdf" in str(exc_info.value.details)

    def test_download_invalid_url_raises_error(self):
        """Test that invalid URL raises error."""
        from app.scraper.downloader import PDFDownloader

        downloader = PDFDownloader()
        downloader.MAX_RETRIES = 1

        with pytest.raises(PDFDownloadError):
            downloader.download_pdf_sync("http://localhost:99999/fake.pdf")


class TestAIProcessorErrorHandling:
    """Tests for AIProcessor error handling."""

    def test_ai_disabled_returns_empty(self):
        """Test that disabled AI returns empty list."""
        from app.scraper.ai_processor import AIProcessor

        with patch.object(AIProcessor, "__init__", lambda self: None):
            processor = AIProcessor()
            processor.enabled = False

            result = processor.process_messy_rows("test", "2025-01-20")
            assert result == []

    def test_ai_short_input_returns_empty(self):
        """Test that very short input returns empty."""
        from app.scraper.ai_processor import AIProcessor

        with patch.object(AIProcessor, "__init__", lambda self: None):
            processor = AIProcessor()
            processor.enabled = True

            result = processor.process_messy_rows("short", "2025-01-20")
            assert result == []

    def test_normalize_empty_name_returns_original(self):
        """Test normalization of empty name."""
        from app.scraper.ai_processor import AIProcessor

        with patch.object(AIProcessor, "__init__", lambda self: None):
            processor = AIProcessor()
            processor.enabled = True

            result = processor.normalize_commodity_name("")
            assert result == ""
