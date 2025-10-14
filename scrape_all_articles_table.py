"""
Scrape the entire КоАП table from shtrafy-gibdd.ru
This gives us ALL articles at once!
"""
import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://shtrafy-gibdd.ru/koap"

print("="*80)
print("SCRAPING ENTIRE КоАП TABLE")
print("="*80)
print(f"\nFetching: {BASE_URL}\n")

try:
    response = requests.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table with articles
    articles_found = {}
    
    # Look for links in the format /koap/12-8-1
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        
        if '/koap/' in href and href != '/koap/':
            # Extract article number from URL
            match = re.search(r'/koap/(\d+-\d+(?:-\d+)?)', href)
            if match:
                url_slug = match.group(1)
                
                # Convert back to article number (12-8-1 -> 12.8)
                article_num = url_slug.split('-')[0] + '.' + url_slug.split('-')[1]
                
                # Get the link text (description)
                text = link.get_text().strip()
                
                if article_num not in articles_found:
                    articles_found[article_num] = {
                        'url_slug': url_slug,
                        'description': text[:100] if text else ''
                    }
    
    print(f"✅ Found {len(articles_found)} articles!\n")
    
    # Show first 20
    print("Sample of articles found:")
    print("-"*80)
    
    count = 0
    for article_num in sorted(articles_found.keys()):
        info = articles_found[article_num]
        print(f"{article_num:8} → {info['url_slug']:15} | {info['description'][:50]}")
        count += 1
        if count >= 20:
            print(f"... and {len(articles_found) - 20} more")
            break
    
    # Save to JSON
    output = {
        'source': BASE_URL,
        'total_articles': len(articles_found),
        'articles': articles_found
    }
    
    with open('koap_articles_map.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Saved all {len(articles_found)} articles to: koap_articles_map.json")
    
    # Generate Python dict
    print("\n" + "="*80)
    print("PYTHON DICT FOR SCRAPER:")
    print("="*80)
    print("\nARTICLE_URLS = {")
    
    count = 0
    for article_num in sorted(articles_found.keys()):
        url_slug = articles_found[article_num]['url_slug']
        print(f'    "{article_num}": "{url_slug}",')
        count += 1
        if count >= 30:
            print(f'    # ... and {len(articles_found) - 30} more')
            break
    
    print("}")
    
    print("\n" + "="*80)
    print(f"✅ SUCCESS - Scraped {len(articles_found)} articles from table!")
    print("="*80)
    print("\nNow the scraper can use this complete mapping!")
    print("No more guessing URLs - we have them all! 🚀")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
