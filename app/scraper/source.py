import logging
import re
from typing import List

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MonitoringSource:
    BASE_URL = "https://www.da.gov.ph/price-monitoring/"

    @staticmethod
    def get_latest_pdf_links() -> List[str]:
        """
        Scrapes the DA monitoring page for Daily Retail Price Range PDFs.
        Only returns Price-Monitoring PDFs (not Daily-Price-Index or Cigarette).
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(follow_redirects=True, timeout=30.0, headers=headers) as client:
                response = client.get(MonitoringSource.BASE_URL)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=re.compile(r"\.pdf$", re.IGNORECASE))

            pdf_urls = []
            for link in links:
                url = link.get("href")
                url_lower = url.lower()

                # Only match "Price-Monitoring" PDFs (Daily Retail Price Range)
                # Exclude Daily-Price-Index and Cigarette monitoring
                if "price-monitoring" in url_lower:
                    if "daily-price-index" not in url_lower and "cigarette" not in url_lower:
                        pdf_urls.append(url)
                        logger.info(f"Found PDF: {url}")

            logger.info(f"Total PDFs found: {len(pdf_urls)}")
            return pdf_urls
        except Exception as e:
            logger.error(f"Failed to scrape monitoring page: {e}")
            return []

    @staticmethod
    def get_new_pdf_links(processed_files: List[str]) -> List[str]:
        """
        Returns only PDFs that haven't been processed yet.
        """
        all_links = MonitoringSource.get_latest_pdf_links()
        new_links = []

        for url in all_links:
            # Extract filename from URL
            filename = url.split("/")[-1]
            if filename not in processed_files:
                new_links.append(url)

        logger.info(f"New PDFs to process: {len(new_links)}")
        return new_links
