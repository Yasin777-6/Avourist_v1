"""
Standalone test of КоАП scraper (no Django)
"""
import requests
from bs4 import BeautifulSoup
import re

def extract_fine(text):
    """Extract fine amount"""
    patterns = [
        r'(\d+)\s*000\s*руб',
        r'(\d+)\s*тысяч',
        r'штраф[^\d]*(\d+)\s*000',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = int(match.group(1)) * 1000
            return f"{amount:,} ₽".replace(',', ' ')
    return None

def extract_license_suspension(text):
    """Extract license suspension"""
    patterns = [
        r'от\s*(\d+[,\.]?\d*)\s*до\s*(\d+)\s*лет',  # "от 1,5 до 2 лет"
        r'от\s*(\d+[,\.]?\d*)\s*до\s*(\d+)\s*года',  # "от 1,5 до 2 года"
        r'от\s*(\d+)\s*до\s*(\d+)\s*месяцев',  # "от 4 до 6 месяцев"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            period_from = match.group(1).replace(',', '.')
            period_to = match.group(2).replace(',', '.')
            if 'месяц' in match.group(0):
                return f"{period_from}-{period_to} месяцев"
            else:
                return f"{period_from}-{period_to} года"
    return None

def test_article(article_num, url_slug):
    """Test scraping a specific article"""
    url = f"https://shtrafy-gibdd.ru/koap/{url_slug}"
    
    print(f"\n{'='*80}")
    print(f"Testing Article {article_num}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text()
        
        # Save for debugging
        with open(f'debug_{article_num}.txt', 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Extract info
        fine = extract_fine(full_text)
        license_suspension = extract_license_suspension(full_text)
        
        # Debug
        print(f"\n🔍 Debug: Searching for license suspension...")
        import re
        test_match = re.search(r'от\s*(\d+[,\.]?\d*)\s*до\s*(\d+)\s*лет', full_text)
        if test_match:
            print(f"   Found match: {test_match.group(0)}")
            print(f"   Groups: {test_match.groups()}")
        
        print(f"\n📋 Article: ст.{article_num} КоАП РФ")
        
        if fine:
            print(f"💰 Fine: {fine}")
        else:
            print(f"❌ Fine: Not found")
        
        if license_suspension:
            print(f"🚫 License Suspension: {license_suspension}")
        else:
            print(f"❌ License Suspension: Not found")
        
        if fine or license_suspension:
            print(f"\n✅ SUCCESS - Data extracted!")
            return True
        else:
            print(f"\n❌ FAILED - No data extracted")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

# Test articles
print("\n🚀 КоАП Scraper Standalone Test")
print("Testing shtrafy-gibdd.ru\n")

results = []
results.append(test_article("12.8", "12-8-1"))
results.append(test_article("12.26", "12-26-1"))

print(f"\n{'='*80}")
print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
print(f"{'='*80}\n")

if all(results):
    print("✅ All tests PASSED! Scraper is working correctly.\n")
else:
    print("⚠️  Some tests failed. Check output above.\n")
