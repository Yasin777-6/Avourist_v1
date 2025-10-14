"""
Scrape the table directly - it has fines right there!
No need to visit individual pages
"""
import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://shtrafy-gibdd.ru/koap"

print("="*80)
print("SCRAPING TABLE WITH FINES DIRECTLY")
print("="*80)

all_articles = {}

# Scrape all pages (1-4)
for page in range(1, 5):
    url = f"{BASE_URL}?page={page}" if page > 1 else BASE_URL
    
    print(f"\n📄 Fetching page {page}: {url}")
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find table rows
        rows_found = 0
        
        # Look for table structure
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            
            if len(cells) >= 3:
                # Column 1: Article number
                article_cell = cells[0].get_text().strip()
                
                # Column 2: Description
                description = cells[1].get_text().strip()
                
                # Column 3: Fine/Punishment
                punishment = cells[2].get_text().strip()
                
                # Extract article number
                article_match = re.search(r'(\d+\.\d+(?:\s*ч\.\d+)?)', article_cell)
                if article_match:
                    article_num = article_match.group(1).replace(' ', '')
                    
                    # Extract fine amount
                    fine = None
                    
                    # Try to find fine in rubles
                    fine_patterns = [
                        r'(\d+)\s*руб',
                        r'(\d+)\s*000\s*руб',
                        r'от\s*(\d+)\s*до\s*(\d+)\s*руб',
                    ]
                    
                    for pattern in fine_patterns:
                        match = re.search(pattern, punishment, re.IGNORECASE)
                        if match:
                            if len(match.groups()) >= 2 and match.group(2):
                                fine = f"{match.group(1)}-{match.group(2)} ₽"
                            else:
                                fine = f"{match.group(1)} ₽"
                            break
                    
                    all_articles[article_num] = {
                        'description': description[:100],
                        'punishment': punishment[:150],
                        'fine': fine
                    }
                    rows_found += 1
        
        print(f"   ✅ Found {rows_found} articles on page {page}")
        
    except Exception as e:
        print(f"   ❌ Error on page {page}: {e}")

print(f"\n{'='*80}")
print(f"✅ TOTAL: Scraped {len(all_articles)} articles with fines!")
print("="*80)

# Show sample
print("\nSample of scraped data:")
print("-"*80)

count = 0
for article_num in sorted(all_articles.keys()):
    info = all_articles[article_num]
    print(f"{article_num:10} | Fine: {info['fine'] or 'N/A':20} | {info['description'][:40]}")
    count += 1
    if count >= 20:
        print(f"... and {len(all_articles) - 20} more")
        break

# Save to JSON
output = {
    'source': BASE_URL,
    'total_articles': len(all_articles),
    'scraped_date': '2025-10-14',
    'articles': all_articles
}

with open('koap_fines_complete.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n💾 Saved to: koap_fines_complete.json")
print("\n" + "="*80)
print("✅ SUCCESS - Now we have ALL fines without visiting individual pages!")
print("="*80)
