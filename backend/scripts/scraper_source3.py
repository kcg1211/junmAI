from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import time
import json

load_dotenv()

SOURCE_URL = os.getenv('WS_SOURCE3_URL')
OUTPUT_FILE = 'source3_data.jsonl'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# TODO: refactoring get_metadata and get_full_text into classes

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
        
# print(get_article_metadata())

def scrape_full_text(article_url):
    """Step 2: Visit the URL and get the actual body text."""
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Locating the main body
        body_container = soup.find('div', class_ = 'l-single-body')
        if not body_container:
            print(f"Warning: No content container found for {article_url}")
            return ""
        
        # Remove the breadcrumb element entirely before processing
        breadcrumb = body_container.find('p', id='breadcrumbs')
        if breadcrumb:
            breadcrumb.decompose()
    
        # 2. Get text from paragraphs that are DIRECT children of l-single-body
        paragraphs = body_container.find_all('p', recursive=False)
        
        processed_paragraphs = []
        
        for p in paragraphs:
            # get_text() pulls text from <span> and <a> tags automatically
            text = p.get_text(strip=True) # strip=True will automatically convert &nbsp; into standard whitespace
            
            # Filter out specific phrases for newsletter subscription
            is_newsletter_prompt = "register here" in text.lower()
            
            if text and not is_newsletter_prompt:
                processed_paragraphs.append(text)
                
            cleaned_content = "\n\n".join(processed_paragraphs)
            return cleaned_content
        
    except Exception as e:
        print(f"Error scraping content for {article_url}: {e}")
        return ""

def scrape_source3():
    # --- MAIN EXECUTION ---
    if __name__ == "__main__":
        # 1. Collect all links
        print("Starting metadata collection...")
        article_list = get_article_metadata()
        # print(article_list)
        print(f"Found {len(article_list)} unique articles.\n")
        
        # 2. Check what have been already scraped
        processed_urls = set()
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        existing_article = json.loads(line)
                        processed_urls.add(existing_article['url'])
                    except json.JSONDecodeError:
                        continue
            print(f"Resuming: {len(processed_urls)} articles already processed. Skipping them.")

        # 3. Scrape full content for each link
        print("Starting full-text extraction (this will take a while)...")
        
        try:
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                for index, article in enumerate(article_list):
                    url = article['url']
                    
                    # --- THE SKIP LOGIC ---
                    if url in processed_urls:
                        continue
                    
                    print(f"[{index+1}/{len(article_list)}] Scraping: {article['title']}")
                    
                    article['full_text'] = scrape_full_text(article['url'])
                    
                    # Write this specific article to a new line in the file
                    json_record = json.dumps(article, ensure_ascii=False)
                    f.write(json_record + "\n")
                    
                    # Flush ensures the data is written to disk immediately
                    f.flush()
                    
                    # Crucial: Sleep to avoid being blocked
                    time.sleep(1.5)
                    
            print(f"\nSuccess! Data saved to {OUTPUT_FILE}")     
        except IOError as e:
            print(f"Error writing to file: {e}")  
        
scrape_source3()