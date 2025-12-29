import json
from collections import Counter

def analyze_exclusions():
    with open('all_da_pdf_links.json', 'r') as f:
        all_links = json.load(f)
    with open('filtered_da_retail_prices.json', 'r') as f:
        filtered_links = json.load(f)
        
    filtered_urls = {item['url'] for item in filtered_links}
    excluded = [item for item in all_links if item['url'] not in filtered_urls]
    
    print(f"Total Excluded: {len(excluded)}")
    
    # Analyze by keyword
    keywords = ["weekly", "index", "cigarette", "visayas", "mindanao", "summary", "outlook", "situationer", "monthly"]
    exclusion_reasons = Counter()
    
    others = []
    for item in excluded:
        text = (item.get('text') or '').lower()
        url = (item.get('url') or '').lower()
        reason_found = False
        for k in keywords:
            if k in text or k in url:
                exclusion_reasons[k] += 1
                reason_found = True
                break
        if not reason_found:
            exclusion_reasons["other/no_date"] += 1
            if len(others) < 5:
                others.append(item)

    print("\nExclusion Reasons:")
    for k, count in sorted(exclusion_reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"- {k}: {count}")
    
    if others:
        print("\nExamples of 'Other' exclusions:")
        for o in others:
            print(f"- {o['text']} | {o['url']}")

if __name__ == "__main__":
    analyze_exclusions()
