import json
from collections import Counter

def verify_data():
    try:
        with open('filtered_da_retail_prices.json', 'r') as f:
            data = json.load(f)
        
        years = [item['date'][:4] for item in data if item.get('date')]
        counts = Counter(years)
        
        print(f"Total entries: {len(data)}")
        print("\nYearly Distribution:")
        for year in sorted(counts.keys()):
            print(f"- {year}: {counts[year]} reports")
            
        # Check for gaps (e.g., if a month is missing)
        months = [item['date'][:7] for item in data if item.get('date')]
        month_counts = Counter(months)
        
        # Just print summary of months if there's no major gap
        all_months = sorted(month_counts.keys())
        if all_months:
            print(f"\nDate Range: {all_months[0]} to {all_months[-1]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_data()
