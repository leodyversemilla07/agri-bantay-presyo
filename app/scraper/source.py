import httpx
from bs4 import BeautifulSoup
from typing import List
import logging
import re

logger = logging.getLogger(__name__)


class MonitoringSource:
    BASE_URL = "https://www.da.gov.ph/price-monitoring/"

    @staticmethod
    def get_latest_pdf_links() -> List[str]:
        """
        Scrapes the DA monitoring page for latest Daily Retail Price PDF links.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(
                follow_redirects=True, timeout=30.0, headers=headers
            ) as client:
                response = client.get(MonitoringSource.BASE_URL)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=re.compile(r"\.pdf$"))

            pdf_urls = []
            for link in links:
                url = link.get("href")
                text = link.get_text().lower()

                if (
                    "dpi" in text
                    or "daily-price-index" in text
                    or "daily prevailing" in text
                ):
                    pdf_urls.append(url)

            return pdf_urls
        except Exception as e:
            logger.error(f"Failed to scrape monitoring page: {e}")
            return []
