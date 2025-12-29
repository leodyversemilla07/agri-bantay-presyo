import json

def check_missed_2019():
    with open('all_da_pdf_links.json', 'r') as f:
        all_links = json.load(f)
    with open('filtered_da_retail_prices.json', 'r') as f:
        filtered_links = json.load(f)
        
    filtered_urls = {item['url'] for item in filtered_links}
    missed_2020 = [item for item in all_links if item.get('date') and item['date'].startswith('2020') and item['url'] not in filtered_urls]
    
    print(f"Missed entries for 2020: {len(missed_2020)}")
    for item in missed_2020[:30]:
        print(f"- {item['text']} | {item['url']}")

if __name__ == "__main__":
    check_missed_2019()
