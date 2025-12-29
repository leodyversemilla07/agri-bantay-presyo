import httpx, re, json
from bs4 import BeautifulSoup

def dump_all():
    r = httpx.get('https://www.da.gov.ph/price-monitoring/', follow_redirects=True, timeout=60.0)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'\.pdf$'))
    data = []
    for l in links:
        data.append({
            "text": l.get_text().strip(),
            "url": l.get('href')
        })
    with open("raw_links_dump.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    dump_all()
