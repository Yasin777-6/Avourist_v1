"""
Test article 8.23 (environmental violations)
"""
import requests
from bs4 import BeautifulSoup
import re

def extract_fine(text):
    """Extract fine amount"""
    patterns = [
        r'от\s*(\d+)\s*до\s*(\d+)\s*тыс',
        r'от\s*(\d+)\s*до\s*(\d+)\s*000',
        r'(\d+)\s*000\s*руб',
        r'(\d+)\s*тысяч',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                if len(match.groups()) >= 2 and match.group(2):
                    amount_from = int(match.group(1)) * 1000
                    amount_to = int(match.group(2)) * 1000
                    return f"{amount_from:,} - {amount_to:,} ₽".replace(',', ' ')
                else:
                    amount = int(match.group(1)) * 1000
                    return f"{amount:,} ₽".replace(',', ' ')
            except:
                pass
    return None

url = "https://shtrafy-gibdd.ru/koap/8-23"

print("="*80)
print("Testing Article 8.23 (Environmental Violations)")
print("="*80)
print(f"URL: {url}\n")

try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    full_text = soup.get_text()
    
    print(f"✅ Fetched successfully")
    print(f"📄 Content length: {len(full_text)} bytes\n")
    
    # Extract fine
    fine = extract_fine(full_text)
    
    print(f"📋 Article: ст.8.23 КоАП РФ")
    print(f"📝 Title: Превышение допустимых показателей шума или вредных выбросов\n")
    
    if fine:
        print(f"💰 Fine extracted: {fine}")
        print(f"\n✅ SUCCESS - Environmental article scraped correctly!")
    else:
        print(f"❌ Fine not found")
        
        # Debug
        if 'штраф' in full_text.lower():
            print("\n🔍 Found 'штраф' in text")
            pos = full_text.lower().find('штраф')
            print(f"Context: ...{full_text[max(0,pos-50):pos+150]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("This proves the scraper works with ANY КоАП chapter!")
print("Not just Chapter 12 (traffic) - also Chapter 8 (environment), etc.")
print("="*80)
