from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import json

load_dotenv()

SOURCE_URL = os.getenv('WS_SOURCE2_URL')
OUTPUT_DIR = './data/processed'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'source2_data.json')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# print("Starting glossary extraction (this will take a while)...")

def scrape_source2():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    # select all divs with class (CSS selector) 'kb'
    items = soup.select('div.kb')

    glossary_data = []

    for item in items:
        try:
            # Extract term - check if h3 exists
            term_el = item.select_one('h3')
            term = term_el.get_text(strip=True) if term_el else "Unknown Term"

            # Extract description - check if p exists
            desc_el = item.select_one('.detail .text p')
            description = desc_el.get_text(strip=True) if desc_el else "No description available."

            # Append as dictionary
            glossary_data.append({
                "term": term,
                "description": description
            })

        except Exception as e:
            print(f"Error processing an item: {e}")
            continue

    # Export to JSON file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(glossary_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved {len(glossary_data)} items to source2_data.json")
    except IOError as e:
        print(f"Error writing to file: {e}")
        
scrape_source2()