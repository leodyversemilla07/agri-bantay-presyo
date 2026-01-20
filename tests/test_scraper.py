"""
Tests for scraper components (parser, downloader, source).
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from app.scraper.downloader import PDFDownloader
from app.scraper.parser import PriceParser
from app.scraper.source import MonitoringSource


class TestPriceParser:
    """Tests for PriceParser class."""

    def test_parser_initialization(self):
        """Test parser initializes with map.json."""
        parser = PriceParser()
        assert parser.normalization_map is not None
        assert len(parser.normalization_map) > 0

    def test_normalize_commodity_known(self):
        """Test normalizing a known commodity name."""
        parser = PriceParser()
        # Test a mapping that exists in map.json
        result = parser.normalize_commodity("Bangus")
        assert result == "Bangus"

    def test_normalize_commodity_with_alias(self):
        """Test normalizing a commodity alias."""
        parser = PriceParser()
        result = parser.normalize_commodity("Milkfish (Bangus)")
        assert result == "Bangus"

    def test_normalize_commodity_unknown(self):
        """Test normalizing an unknown commodity returns original."""
        parser = PriceParser()
        result = parser.normalize_commodity("Unknown Commodity XYZ")
        assert result == "Unknown Commodity XYZ"

    def test_normalize_commodity_empty(self):
        """Test normalizing empty string."""
        parser = PriceParser()
        result = parser.normalize_commodity("")
        assert result == ""

    def test_normalize_commodity_whitespace(self):
        """Test normalizing string with extra whitespace."""
        parser = PriceParser()
        result = parser.normalize_commodity("  Bangus  ")
        # Should handle whitespace
        assert "Bangus" in result

    def test_is_category_row_true(self):
        """Test identifying category rows."""
        parser = PriceParser()
        # Category rows have ALL CAPS in first column with no data in other columns
        row = ["VEGETABLES", None, None, None]
        assert parser.is_category_row(row) is True

    def test_is_category_row_false(self):
        """Test non-category rows."""
        parser = PriceParser()
        row = ["Tomato", "45.00", "55.00", "50.00"]
        assert parser.is_category_row(row) is False

    def test_parse_numeric_valid(self):
        """Test parsing valid numeric strings."""
        parser = PriceParser()
        assert parser._parse_numeric("45.00") == 45.00
        assert parser._parse_numeric("1,234.56") == 1234.56

    def test_parse_numeric_invalid(self):
        """Test parsing invalid numeric strings."""
        parser = PriceParser()
        assert parser._parse_numeric("N/A") is None
        assert parser._parse_numeric("-") is None
        assert parser._parse_numeric("") is None
        assert parser._parse_numeric(None) is None

    def test_extract_date_from_text(self):
        """Test extracting date from text."""
        parser = PriceParser()

        text = "Daily Price Monitoring Report for December 27, 2025"
        result = parser.extract_date_from_text(text)

        assert result is not None
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 27

    def test_extract_date_alternative_format(self):
        """Test extracting date in alternative format."""
        parser = PriceParser()

        text = "Report dated 27 December 2025"
        result = parser.extract_date_from_text(text)

        assert result is not None
        assert result.day == 27

    def test_extract_date_no_date(self):
        """Test extracting date when none present."""
        parser = PriceParser()
        result = parser.extract_date_from_text("No date here")
        assert result is None


class TestPDFDownloader:
    """Tests for PDFDownloader class."""

    def test_downloader_initialization(self):
        """Test downloader creates download directory."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = PDFDownloader(download_dir=tmpdir)
            assert downloader.download_dir.exists()

    def test_downloader_default_directory(self):
        """Test downloader uses default directory."""
        downloader = PDFDownloader()
        assert downloader.download_dir == Path("downloads")

    def test_list_downloaded_pdfs_empty(self):
        """Test listing PDFs in empty directory."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = PDFDownloader(download_dir=tmpdir)
            result = downloader.list_downloaded_pdfs()
            assert result == []

    def test_list_downloaded_pdfs(self):
        """Test listing PDFs in directory."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fake PDF files
            Path(tmpdir, "test1.pdf").touch()
            Path(tmpdir, "test2.pdf").touch()
            Path(tmpdir, "not_pdf.txt").touch()

            downloader = PDFDownloader(download_dir=tmpdir)
            result = downloader.list_downloaded_pdfs()

            assert len(result) == 2
            assert all(str(p).endswith(".pdf") for p in result)


class TestMonitoringSource:
    """Tests for MonitoringSource class."""

    def test_base_url(self):
        """Test base URL is correct."""
        assert MonitoringSource.BASE_URL == "https://www.da.gov.ph/price-monitoring/"

    @patch("app.scraper.source.httpx.Client")
    def test_get_latest_pdf_links_filters_correctly(self, mock_client):
        """Test that PDF link filtering works correctly."""
        # Mock response with various PDF types
        mock_response = Mock()
        mock_response.text = """
        <html>
        <a href="https://da.gov.ph/Price-Monitoring-Dec-2025.pdf">Daily</a>
        <a href="https://da.gov.ph/Daily-Price-Index-Dec-2025.pdf">DPI</a>
        <a href="https://da.gov.ph/Cigarette-Monitoring.pdf">Cig</a>
        </html>
        """
        mock_response.raise_for_status = Mock()

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        result = MonitoringSource.get_latest_pdf_links()

        # Should only include Price-Monitoring, not DPI or Cigarette
        assert len(result) == 1
        assert "Price-Monitoring" in result[0]

    def test_get_new_pdf_links_filters_processed(self):
        """Test filtering out already processed files."""
        with patch.object(MonitoringSource, "get_latest_pdf_links") as mock_get:
            mock_get.return_value = [
                "https://da.gov.ph/file1.pdf",
                "https://da.gov.ph/file2.pdf",
                "https://da.gov.ph/file3.pdf",
            ]

            processed = ["file1.pdf", "file2.pdf"]
            result = MonitoringSource.get_new_pdf_links(processed)

            assert len(result) == 1
            assert "file3.pdf" in result[0]
