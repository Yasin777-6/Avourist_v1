"""
Verify all fines in knowledge base using scraper
"""
import requests
from bs4 import BeautifulSoup
import re
import json

def extract_fine(text):
    """Extract fine amount"""
    patterns = [
        r'(\d+)\s*000\s*руб',
        r'(\d+)\s*тысяч',
        r'штраф[^\d]*(\d+)\s*000',
        r'(\d+)\s*рублей',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(' ', '')
            try:
                amount = int(amount_str)
                if '000' in match.group(0):
                    amount = amount * 1000
                elif 'тысяч' in match.group(0):
                    amount = amount * 1000
                return f"{amount:,} ₽".replace(',', ' ')
            except:
                pass
    return None

def extract_license_suspension(text):
    """Extract license suspension"""
    patterns = [
        r'от\s*(\d+[,\.]?\d*)\s*до\s*(\d+)\s*лет',
        r'от\s*(\d+)\s*до\s*(\d+)\s*месяцев',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            period_from = match.group(1).replace(',', '.')
            period_to = match.group(2)
            if 'месяц' in match.group(0):
                return f"{period_from}-{period_to} месяцев"
            else:
                return f"{period_from}-{period_to} года"
    return None

def scrape_article(article_num, url_slug):
    """Scrape article from shtrafy-gibdd.ru"""
    url = f"https://shtrafy-gibdd.ru/koap/{url_slug}"
    
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0'
        }, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text()
        
        fine = extract_fine(full_text)
        license_suspension = extract_license_suspension(full_text)
        
        return {
            'fine': fine,
            'license_suspension': license_suspension,
            'url': url
        }
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# Articles to verify
articles_to_check = [
    ("12.8", "12-8-1", "ч.1 ст.12.8 КоАП РФ", "Drunk driving"),
    ("12.26", "12-26-1", "ч.1 ст.12.26 КоАП РФ", "Refusal to test"),
    ("12.7", "12-7", "ч.1 ст.12.7 КоАП РФ", "Driving without license"),
    ("12.9", "12-9", "ч.3-5 ст.12.9 КоАП РФ", "Speeding"),
    ("12.15", "12-15", "ч.4 ст.12.15 КоАП РФ", "Wrong lane"),
]

print("="*80)
print("VERIFYING ALL FINES FROM shtrafy-gibdd.ru")
print("="*80)

results = []

for article_num, url_slug, full_code, description in articles_to_check:
    print(f"\n📋 {full_code} - {description}")
    print("-"*80)
    
    scraped = scrape_article(article_num, url_slug)
    
    if scraped:
        if scraped['fine']:
            print(f"   💰 Fine: {scraped['fine']}")
        else:
            print(f"   ⚠️  Fine: Not found")
        
        if scraped['license_suspension']:
            print(f"   🚫 License: {scraped['license_suspension']}")
        else:
            print(f"   ℹ️  License: Not applicable or not found")
        
        print(f"   🔗 Source: {scraped['url']}")
        
        results.append({
            'article': full_code,
            'scraped': scraped
        })
    else:
        print(f"   ❌ Failed to scrape")

# Load current knowledge base
print(f"\n\n{'='*80}")
print("COMPARING WITH KNOWLEDGE BASE")
print("="*80)

with open('ai_engine/data/koap_articles.json', 'r', encoding='utf-8') as f:
    kb = json.load(f)

for result in results:
    article_code = result['article']
    scraped = result['scraped']
    
    # Find in KB
    kb_article = None
    for article in kb['articles']:
        if article['article'] == article_code:
            kb_article = article
            break
    
    if kb_article:
        print(f"\n📋 {article_code}")
        
        kb_fine = kb_article['punishment'].get('fine', 'N/A')
        scraped_fine = scraped.get('fine', 'N/A')
        
        if kb_fine == scraped_fine:
            print(f"   ✅ Fine matches: {kb_fine}")
        else:
            print(f"   ⚠️  Fine mismatch!")
            print(f"      KB: {kb_fine}")
            print(f"      Scraped: {scraped_fine}")
        
        kb_license = kb_article['punishment'].get('license_suspension', 'N/A')
        scraped_license = scraped.get('license_suspension', 'N/A')
        
        if kb_license and scraped_license:
            # Normalize for comparison
            kb_norm = kb_license.replace(' ', '').replace('-', '').lower()
            scraped_norm = scraped_license.replace(' ', '').replace('-', '').lower()
            
            if kb_norm == scraped_norm or kb_license == scraped_license:
                print(f"   ✅ License matches: {kb_license}")
            else:
                print(f"   ⚠️  License mismatch!")
                print(f"      KB: {kb_license}")
                print(f"      Scraped: {scraped_license}")

print(f"\n{'='*80}")
print("✅ VERIFICATION COMPLETE")
print("="*80)
print("\nCheck output above for any mismatches that need updating.\n")
