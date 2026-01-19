from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import time
import json

load_dotenv()

SOURCE_URL = os.getenv('WS_SOURCE3_URL')
OUTPUT_FILE = 'source3_data.json'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_article_metadata():
    """Step 1: Get URLs and Titles."""
    articles = []
    
    categories_slugs = [
    "learn",
    "brewery-stories",
    "how-to-drink/pairings",
    "how-to-drink/drinking-at-home",
    "deep-dive/sake-vs-wine"
    ]
    
    for slugs in categories_slugs:
        target_url = f"{SOURCE_URL}category/{slugs}"
        print(f"Fetching: {target_url}...")
    
        try:
            response = requests.get(target_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')  
            article_links = soup.select('.l-main-column-area .article-title a') # Find all tags with the CSS selector '.article-title' and the <a> tag inside, under the '.l-main-column-area'

            for link in article_links:
                title = link.get_text(strip=True)
                url = link.get('href')

                if title and url:
                    articles.append({
                        "title": title,
                        "url": url,
                        "category": slugs
                    })

            time.sleep(1.5)
            
        except Exception as e:
            print(f"Could not retrieve category '{slugs}': {e}")

    return articles
        
print(get_article_metadata())
    
    