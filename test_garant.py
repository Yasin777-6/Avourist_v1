"""
Test scraping from garant.ru
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://base.garant.ru/12125267/"

print("="*80)
print("Testing garant.ru")
print("="*80)
print(f"\n📡 Fetching: {url}\n")

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    print(f"✅ Response: {response.status_code}")
    print(f"📄 Content length: {len(response.text)} bytes\n")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    full_text = soup.get_text()
    
    # Search for article 12.8
    print("🔍 Searching for article 12.8...")
    
    search_terms = ['Статья 12.8', 'статья 12.8', '12.8']
    pos = -1
    
    for term in search_terms:
        pos = full_text.find(term)
        if pos != -1:
            print(f"✅ Found '{term}' at position {pos}\n")
            break
    
    if pos != -1:
        # Extract section
        article_section = full_text[pos:pos+2500]
        
        print("="*80)
        print("ARTICLE 12.8 SECTION:")
        print("="*80)
        print(article_section)
        print("="*80)
        
        # Save to file for analysis
        with open('garant_article_12_8.txt', 'w', encoding='utf-8') as f:
            f.write(article_section)
        print("\n💾 Saved to garant_article_12_8.txt")
        
        # Extract fine
        print("\n💰 Extracting fine...")
        fine_patterns = [
            r'(\d+)\s+тысяч рублей',
            r'(\d+)\s+тыс\.\s+рублей',
            r'штраф.*?(\d+)\s+тысяч',
            r'административный штраф.*?(\d+)\s+тысяч',
            r'наложение административного штрафа.*?(\d+)\s+тысяч',
        ]
        
        fine_found = False
        for pattern in fine_patterns:
            match = re.search(pattern, article_section, re.IGNORECASE)
            if match:
                amount = int(match.group(1)) * 1000
                print(f"   ✅ Fine: {amount:,} ₽".replace(',', ' '))
                print(f"   Pattern used: {pattern}")
                fine_found = True
                break
        
        if not fine_found:
            print("   ❌ Could not extract fine")
        
        # Extract license suspension
        print("\n🚫 Extracting license suspension...")
        license_patterns = [
            r'лишение права управления.*?на срок от\s+(\d+\.?\d*)\s+до\s+(\d+\.?\d*)\s+(лет|года|месяцев)',
            r'лишение права управления.*?от\s+(\d+\.?\d*)\s+до\s+(\d+\.?\d*)\s+(лет|года|месяцев)',
            r'лишением права управления.*?от\s+(\d+\.?\d*)\s+до\s+(\d+\.?\d*)\s+(лет|года|месяцев)',
            r'лишение.*?от\s+(\d+\.?\d*)\s+до\s+(\d+\.?\d*)\s+(лет|года|месяцев)',
        ]
        
        license_found = False
        for pattern in license_patterns:
            match = re.search(pattern, article_section, re.IGNORECASE)
            if match:
                print(f"   ✅ License suspension: {match.group(1)} - {match.group(2)} {match.group(3)}")
                print(f"   Pattern used: {pattern}")
                license_found = True
                break
        
        if not license_found:
            print("   ❌ Could not extract license suspension")
        
    else:
        print("❌ Article 12.8 not found")
        print("\n📝 Sample content (first 1500 chars):")
        print(full_text[:1500])

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed!\n")
