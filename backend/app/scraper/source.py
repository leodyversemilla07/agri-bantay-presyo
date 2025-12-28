import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)

class MonitoringSource:
    BASE_URL = "https://www.da.gov.ph/price-monitoring/"
    
    @staticmethod
    def get_latest_pdf_links() -> Dict[str, List[str]]:
        """
        Scrapes the DA monitoring page for latest PDF links.
        Returns a dict categorized by type.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(follow_redirects=True, timeout=30.0, headers=headers) as client:
                response = client.get(MonitoringSource.BASE_URL)
                response.raise_for_status()
                
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=re.compile(r'\.pdf$'))
            
            results = {
                "daily": [],
                "weekly": []
            }
            
            for link in links:
                url = link.get('href')
                text = link.get_text().lower()
                
                # Broad matching based on findings
                if any(k in text or k in url.lower() for k in ["dpi", "daily-price-index", "daily prevailing"]):
                    results["daily"].append(url)
                elif any(k in text or k in url.lower() for k in ["weekly-average", "weekly average"]):
                    results["weekly"].append(url)
                    
            return results
        except Exception as e:
            logger.error(f"Failed to scrape monitoring page: {e}")
            return {"daily": [], "weekly": []}
