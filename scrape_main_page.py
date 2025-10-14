"""
Scrape main page to find all article URLs
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://shtrafy-gibdd.ru/koap/"

print("="*80)
print("Scraping Main Page for Article Links")
print("="*80)
print(f"URL: {url}\n")

try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    response.raise_for_status()
    
    print(f"✅ Response: {response.status_code}\n")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links to articles
    article_links = []
    
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        text = link.get_text().strip()
        
        # Look for links that match article patterns
        if '/koap/' in href and re.search(r'12[.-]\d+', href):
            article_links.append({
                'href': href,
                'text': text
            })
    
    # Remove duplicates
    seen = set()
    unique_links = []
    for link in article_links:
        if link['href'] not in seen:
            seen.add(link['href'])
            unique_links.append(link)
    
    print(f"Found {len(unique_links)} article links:\n")
    print("="*80)
    
    # Group by article number
    articles = {}
    for link in unique_links:
        href = link['href']
        text = link['text']
        
        # Extract article number
        match = re.search(r'12[.-](\d+)(?:[.-](\d+))?', href)
        if match:
            article_num = f"12.{match.group(1)}"
            part = match.group(2) if match.group(2) else "1"
            
            if article_num not in articles:
                articles[article_num] = []
            
            articles[article_num].append({
                'part': part,
                'url': href,
                'text': text[:80]
            })
    
    # Print organized
    for article_num in sorted(articles.keys()):
        print(f"\n📋 Статья {article_num}:")
        for item in articles[article_num]:
            # Extract slug from URL
            slug = item['url'].split('/koap/')[-1]
            print(f"   ч.{item['part']}: {slug}")
            if item['text']:
                print(f"      {item['text']}")
    
    print("\n" + "="*80)
    print("Python dict for scraper:")
    print("="*80)
    print("\nARTICLE_URLS = {")
    
    # Create mapping for common articles
    common_articles = ['12.7', '12.8', '12.9', '12.15', '12.26']
    for article_num in common_articles:
        if article_num in articles and articles[article_num]:
            slug = articles[article_num][0]['url'].split('/koap/')[-1]
            print(f'    "{article_num}": "{slug}",')
    
    print("}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
