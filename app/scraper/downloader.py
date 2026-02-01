import logging
import time
from pathlib import Path
from typing import List, Optional

import aiofiles
import httpx

from app.core.exceptions import PDFDownloadError

logger = logging.getLogger(__name__)


class PDFDownloader:
    """
    Downloads PDF files with retry logic and error handling.
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    TIMEOUT = 60  # seconds

    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def download_pdf_sync(self, url: str, filename: Optional[str] = None) -> Path:
        """
        Download a PDF file synchronously with retry logic.

        Args:
            url: URL of the PDF to download
            filename: Optional filename to save as

        Returns:
            Path to the downloaded file

        Raises:
            PDFDownloadError: If download fails after all retries
        """
        if not filename:
            filename = url.split("/")[-1]
            # Sanitize filename
            filename = "".join(c for c in filename if c.isalnum() or c in ".-_")

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        target_path = self.download_dir / filename
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Downloading PDF (attempt {attempt + 1}/{self.MAX_RETRIES}): {url}")

                with httpx.Client(
                    timeout=self.TIMEOUT,
                    follow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                ) as client:
                    response = client.get(url)
                    response.raise_for_status()

                    # Verify it's a PDF
                    content_type = response.headers.get("content-type", "")
                    if "pdf" not in content_type.lower() and not response.content[:4] == b"%PDF":
                        raise PDFDownloadError(
                            url=url,
                            reason=f"Response is not a PDF (content-type: {content_type})",
                        )

                    # Check file size (should be at least 1KB for a valid PDF)
                    if len(response.content) < 1024:
                        raise PDFDownloadError(
                            url=url,
                            reason=f"PDF too small ({len(response.content)} bytes)",
                        )

                    with open(target_path, "wb") as f:
                        f.write(response.content)

                    logger.info(f"Successfully downloaded: {target_path} ({len(response.content)} bytes)")
                    return target_path

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Timeout downloading {url} (attempt {attempt + 1})")

            except httpx.HTTPStatusError as e:
                last_error = e
                status_code = e.response.status_code

                # Don't retry on client errors (4xx)
                if 400 <= status_code < 500:
                    raise PDFDownloadError(
                        url=url,
                        reason=f"HTTP {status_code}: {e.response.reason_phrase}",
                    )

                logger.warning(f"HTTP error {status_code} downloading {url} (attempt {attempt + 1})")

            except PDFDownloadError:
                raise  # Re-raise our custom errors

            except Exception as e:
                last_error = e
                logger.warning(f"Error downloading {url} (attempt {attempt + 1}): {e}")

            # Wait before retry with exponential backoff
            if attempt < self.MAX_RETRIES - 1:
                wait_time = self.RETRY_DELAY * (2**attempt)
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        # All retries exhausted
        raise PDFDownloadError(
            url=url,
            reason=f"Failed after {self.MAX_RETRIES} attempts: {str(last_error)}",
        )

    async def download_pdf_async(self, url: str, filename: Optional[str] = None) -> Path:
        """
        Download a PDF file asynchronously with retry logic.

        Args:
            url: URL of the PDF to download
            filename: Optional filename to save as

        Returns:
            Path to the downloaded file

        Raises:
            PDFDownloadError: If download fails after all retries
        """
        import asyncio

        if not filename:
            filename = url.split("/")[-1]
            filename = "".join(c for c in filename if c.isalnum() or c in ".-_")

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        target_path = self.download_dir / filename
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Async downloading PDF (attempt {attempt + 1}/{self.MAX_RETRIES}): {url}")

                async with httpx.AsyncClient(
                    timeout=self.TIMEOUT,
                    follow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                ) as client:
                    response = await client.get(url)
                    response.raise_for_status()

                    # Verify it's a PDF
                    content_type = response.headers.get("content-type", "")
                    if "pdf" not in content_type.lower() and not response.content[:4] == b"%PDF":
                        raise PDFDownloadError(
                            url=url,
                            reason=f"Response is not a PDF (content-type: {content_type})",
                        )

                    async with aiofiles.open(target_path, "wb") as f:
                        await f.write(response.content)

                    logger.info(f"Successfully downloaded: {target_path}")
                    return target_path

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Timeout downloading {url} (attempt {attempt + 1})")

            except httpx.HTTPStatusError as e:
                last_error = e
                if 400 <= e.response.status_code < 500:
                    raise PDFDownloadError(url=url, reason=f"HTTP {e.response.status_code}")
                logger.warning(f"HTTP error downloading {url} (attempt {attempt + 1})")

            except PDFDownloadError:
                raise

            except Exception as e:
                last_error = e
                logger.warning(f"Error downloading {url} (attempt {attempt + 1}): {e}")

            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(self.RETRY_DELAY * (2**attempt))

        raise PDFDownloadError(
            url=url,
            reason=f"Failed after {self.MAX_RETRIES} attempts: {str(last_error)}",
        )

    def list_downloaded_pdfs(self) -> List[Path]:
        """List all downloaded PDF files."""
        return list(self.download_dir.glob("*.pdf"))

    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Remove PDF files older than specified hours.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of files removed
        """
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed = 0

        for pdf_path in self.list_downloaded_pdfs():
            try:
                mtime = datetime.fromtimestamp(pdf_path.stat().st_mtime)
                if mtime < cutoff:
                    pdf_path.unlink()
                    logger.info(f"Removed old file: {pdf_path.name}")
                    removed += 1
            except Exception as e:
                logger.warning(f"Failed to remove {pdf_path}: {e}")

        return removed
