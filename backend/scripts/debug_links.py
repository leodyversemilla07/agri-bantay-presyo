import httpx
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.da.gov.ph/price-monitoring/"

def debug_fetch():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    with httpx.Client(follow_redirects=True, timeout=60.0, headers=headers) as client:
        response = client.get(BASE_URL)
        
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'\.pdf$'))
    
    logger.info(f"debug: Found {len(links)} links.")
    
    count = 0
    for link in links:
        url = link.get('href').lower()
        text = link.get_text().strip().lower()
        
        # Check newer years
        if "2024" in url or "2024" in text:
            logger.info(f"2024 Candidate: TXT='{text}' URL='{url}'")
            count += 1
            if count > 20: break

if __name__ == "__main__":
    debug_fetch()
