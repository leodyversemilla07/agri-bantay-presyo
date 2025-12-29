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
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
QUEUE_FILE = DATA_DIR / "filtered_da_retail_prices.json"
ALL_LINKS_FILE = DATA_DIR / "all_da_pdf_links.json"

def parse_date_from_text(text: str, url: str = None) -> (str, str):
    # Fix common typos in month names
    typos = {
        "Marhc": "March",
        "Augsut": "August",
        "Januay": "January",
        "Febuary": "February",
        "Septempber": "September",
        "Octover": "October"
    }
    
    clean_text = text
    for typo, correct in typos.items():
        clean_text = clean_text.replace(typo, correct)
    
    fixed_text = clean_text # Keep the version with fixed month names
    
    # Remove potential noise for date parsing
    date_parsing_text = clean_text.replace("Price Monitoring", "").replace("Price Watch", "").replace("Daily", "").replace("Price Index", "").strip(", ")
    
    # Try different date formats
    formats = [
        "%B %d, %Y",  # "December 28, 2018"
        "%b %d, %Y",  # "Dec 28, 2018"
        "%B %d %Y",   # "May 17 2019"
        "%b %d %Y",   # "May 17 2019" (abbreviated)
        "%m/%d/%Y",
        "%Y-%m-%d"
    ]
    
    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_parsing_text, fmt).date().isoformat()
            break
        except ValueError:
            continue
            
    # Fallback: Try to extract from URL if text failed
    if not parsed_date and url:
        # e.g. .../2025/12/Price-Monitoring-December-27-2025.pdf
        match = re.search(r'(\d{4})/(\d{2})', url)
        if match:
            year, month = match.groups()
            # Try to find day in filename
            day_match = re.search(r'(\d{1,2})-\d{4}', url)
            if day_match:
                day = day_match.group(1).zfill(2)
                parsed_date = f"{year}-{month}-{day}"
                
    return fixed_text, parsed_date

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
        links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        logger.info(f"Found {len(links)} total PDF links.")
        
        all_candidates = []
        filtered_candidates = []
        
        for link in links:
            url = link.get('href')
            text = link.get_text().strip()
            
            if not url:
                continue
            
            # If text is empty (e.g. image link), try to get it from the URL filename
            if not text:
                text = url.split('/')[-1]
                
            url_lower = url.lower()
            text_lower = text.lower()
            
            # Parse date for everyone
            fixed_text, date_str = parse_date_from_text(text, url)
            
            entry = {
                "url": url,
                "text": fixed_text,
                "date": date_str
            }
            all_candidates.append(entry)
            
            # Normalize for checking: replace dashes and underscores with spaces
            norm_url = url_lower.replace('-', ' ').replace('_', ' ')
            norm_text = text_lower.replace('-', ' ').replace('_', ' ')
            
            # APPLY FILTERS for the restricted list:
            # Strictly target "Daily Retail Price Range"
            is_relevant = False
            
            # Inclusion keywords: things that look like actual price range reports
            # Using partial matches to catch typos like "monitrong"
            include_keywords = ["price watch", "price monitoring", "retail price range", "price range", "daily", "monit", "watch"]
            if any(k in norm_url or k in norm_text for k in include_keywords):
                is_relevant = True
            
            # Exclusion keywords: things that are definitely not what we want
            # Using partial matches to catch "weeky" etc.
            exclude_keywords = ["week", "index", "cigaret", "visayas", "mindanao", "summary", "outlook", "situationer"]
            if any(k in norm_url or k in norm_text for k in exclude_keywords):
                is_relevant = False

            if is_relevant and date_str:
                filtered_candidates.append(entry)
        
        # 1. Save ALL links
        unique_all = {c['url']: c for c in all_candidates}.values()
        sorted_all = sorted(list(unique_all), key=lambda x: x['date'] or '0000-00-00', reverse=False)
        
        with open(ALL_LINKS_FILE, "w") as f:
            json.dump(sorted_all, f, indent=2)
        logger.info(f"Saved ALL {len(sorted_all)} PDF links to {ALL_LINKS_FILE}")

        # 2. Save FILTERED links
        unique_filtered = {c['url']: c for c in filtered_candidates}.values()
        sorted_filtered = sorted(list(unique_filtered), key=lambda x: x['date'], reverse=False)
        
        with open(QUEUE_FILE, "w") as f:
            json.dump(sorted_filtered, f, indent=2)
            
        logger.info(f"Saved {len(sorted_filtered)} strictly filtered Retail Price reports to {QUEUE_FILE}")
        return sorted_filtered

    except Exception as e:
        logger.error(f"Error fetching links: {e}")
        return []

if __name__ == "__main__":
    fetch_links()
