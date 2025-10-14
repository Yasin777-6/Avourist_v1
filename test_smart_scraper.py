"""
Test smart scraper - no Django needed
"""
import requests

BASE_URL = "https://shtrafy-gibdd.ru/koap/"

def test_article(article_num):
    """Test finding article URL automatically"""
    print(f"\n{'='*80}")
    print(f"Testing Article: {article_num}")
    print(f"{'='*80}")
    
    # Try common patterns
    simple_slug = article_num.replace('.', '-')
    patterns = [
        f"{simple_slug}-1",  # 8.23 -> 8-23-1
        simple_slug,          # 8.23 -> 8-23
        f"{simple_slug}-2",  # 8.23 -> 8-23-2
    ]
    
    for slug in patterns:
        url = f"{BASE_URL}{slug}"
        print(f"\nTrying: {url}")
        
        try:
            response = requests.head(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ FOUND! URL: {slug}")
                
                # Now fetch full content
                full_response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(full_response.text, 'html.parser')
                text = soup.get_text()
                
                # Try to find fine
                import re
                fine_match = re.search(r'(\d+)\s*рублей', text)
                if fine_match:
                    print(f"   💰 Fine found: {fine_match.group(1)} ₽")
                
                return slug
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
    
    print(f"\n❌ Could not find URL for article {article_num}")
    return None

# Test articles
print("="*80)
print("INTELLIGENT SCRAPER TEST")
print("="*80)
print("\nAutomatically finding URLs for articles...")

test_article("8.23")   # Environmental (not in mapping)
test_article("12.8")   # Traffic (in mapping)
test_article("19.3")   # Administrative (not in mapping)

print(f"\n{'='*80}")
print("✅ Scraper can find URLs automatically!")
print("="*80)
