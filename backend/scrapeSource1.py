from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import time
import csv
import json

load_dotenv()

# --- CONFIGURATION ---
# BASE_API_URL = "https://api.sakestreet.com/v1/media"
SOURCE_BASE_API_URL = os.getenv('WS_SOURCE1_BASE_API_URL')
SOURCE_URL=os.getenv('WS_SOURCE1_URL')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_all_article_metadata():
    """Step 1: Get URLs and Titles from the API."""
    articles = []
    seen_slugs = set()
    page = 0
    
    # while:
    for _ in range(1):
        print(f"Fetching API page {page}...")
        params = {"base_offset": 9, "page": page, "size": 8, "lang": "en-US"}
        
        try:
            response = requests.get(SOURCE_BASE_API_URL, params=params, headers=HEADERS)
            data = response.json()
            media_items = data.get("media", [])
            
            if not media_items:
                break
            
            new_items_on_this_page = 0
            for item in media_items:
                slug = item.get("slug")
                if slug and slug not in seen_slugs:
                    seen_slugs.add(slug)
                    articles.append({
                        "title": item.get("title"),
                        "url": f"{SOURCE_URL}{slug}",
                        "summary": item.get("summary"),
                        "date": item.get("published_at")
                    })
                    new_items_on_this_page += 1
            
            if new_items_on_this_page == 0:
                print("Detected duplicate data. Stopping API crawl.")
                break
                
            page += 1
            time.sleep(1.5)
        except Exception as e:
            print(f"API Error: {e}")
            break
            
    return articles

def scrape_full_text(url):
    """Step 2: Visit the URL and get the actual body text."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sake Street puts main content in <article> or specific content divs
        # We target paragraphs to keep the text clean
        article_content = soup.find('div', class_ = 'mediaRootEn-0-2-28 mediaRoot-0-2-27')
        paragraphs = article_content.find_all('p')

        # if article_content:
        #     paragraphs = article_content.find_all('p')
        # else:
        #     paragraphs = soup.find_all('p')
            
        text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        return text
    except Exception as e:
        print(f"Error scraping content for {url}: {e}")
        return ""

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Collect all links
    print("Starting metadata collection...")
    article_list = get_all_article_metadata()
    # print(article_list)
    print(f"Found {len(article_list)} unique articles.\n")

    # 2. Scrape full content for each link
    print("Starting full-text extraction (this will take a while)...")
    for index, article in enumerate(article_list):
        print(f"[{index+1}/{len(article_list)}] Scraping: {article['title']}")
        
        article['full_text'] = scrape_full_text(article['url'])
        
        # Crucial: Sleep to avoid being blocked
        time.sleep(1.5)

    # 3. Save to JSON
    output_filename = 'source1_data.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        # ensure_ascii=False keeps Japanese characters readable
        # indent=4 makes the file human-readable
        json.dump(article_list, f, ensure_ascii=False, indent=4)

    print(f"\nSuccess! Data saved to {output_filename}")
    
    # # 3. Save to CSV
    # keys = article_list[0].keys()
    # with open('source1_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
    #     dict_writer = csv.DictWriter(f, fieldnames=keys)
    #     dict_writer.writeheader()
    #     dict_writer.writerows(article_list)

    # print("\nSuccess! Data saved to source1_data.csv")