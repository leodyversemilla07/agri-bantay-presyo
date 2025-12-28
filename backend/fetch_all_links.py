import httpx
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.da.gov.ph/price-monitoring/"
QUEUE_FILE = "backfill_queue.json"

def parse_date_from_text(text: str) -> str:
    # Try different date formats
    try:
        # "December 28, 2018"
        return datetime.strptime(text.strip(), "%B %d, %Y").date().isoformat()
    except ValueError:
        pass
    
    try:
        # "Dec 28, 2018"
        return datetime.strptime(text.strip(), "%b %d, %Y").date().isoformat()
    except ValueError:
        pass
        
    return None

def fetch_links():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    logger.info(f"Fetching {BASE_URL}...")
    try:
        with httpx.Client(follow_redirects=True, timeout=60.0, headers=headers) as client:
            response = client.get(BASE_URL)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all PDF links
        links = soup.find_all('a', href=re.compile(r'\.pdf$'))
        logger.info(f"Found {len(links)} total PDF links.")
        
        candidates = []
        
        for link in links:
            url = link.get('href')
            text = link.get_text().strip()
            
            if not url or not text:
                continue
                
            url_lower = url.lower()
            text_lower = text.lower()
            
            # FILTERS:
            # Must be "Daily" or "Price Watch"
            # Exclude "Weekly", "Index", "Cigarette"
            is_relevant = False
            if "price-watch" in url_lower or "price watch" in text_lower:
                is_relevant = True
            elif "daily" in url_lower or "daily" in text_lower:
                is_relevant = True
            
            if "weekly" in url_lower or "weekly" in text_lower:
                is_relevant = False
            if "index" in url_lower or "index" in text_lower:
                is_relevant = False
            if "cigarette" in url_lower or "cigarette" in text_lower:
                is_relevant = False
            if "visayas" in url_lower or "mindanao" in url_lower:
                 # Usually we want Metro Manila/National, unless specified. 
                 # Often regional files are separated. We'll stick to generic ones that usually imply MM.
                 pass

            if is_relevant:
                # Try to parse date from link text
                date_str = parse_date_from_text(text)
                
                candidates.append({
                    "url": url,
                    "text": text,
                    "date": date_str
                })
        
        # Deduplicate by URL
        unique_candidates = {c['url']: c for c in candidates}.values()
        sorted_candidates = sorted(list(unique_candidates), key=lambda x: x['date'] or '0000-00-00', reverse=True)
        
        logger.info(f"Filtered down to {len(sorted_candidates)} relevant daily reports.")
        
        with open(QUEUE_FILE, "w") as f:
            json.dump(sorted_candidates, f, indent=2)
            
        logger.info(f"Saved queue to {QUEUE_FILE}")
        return sorted_candidates

    except Exception as e:
        logger.error(f"Error fetching links: {e}")
        return []

if __name__ == "__main__":
    fetch_links()
