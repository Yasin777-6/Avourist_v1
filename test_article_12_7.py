"""
Test article 12.7 extraction
"""
import requests
from bs4 import BeautifulSoup
import re

def extract_fine(text):
    """Extract fine amount"""
    patterns = [
        # Range patterns
        r'от\s*(\d+)\s*до\s*(\d+)\s*тыс',
        r'от\s*(\d+)\s*до\s*(\d+)\s*000',
        r'от\s*(\d+[\s\d]+)\s*до\s*(\d+[\s\d]+)\s*руб',
        # Single amount
        r'(\d+)\s*000\s*руб',
        r'(\d+)\s*тысяч',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Check if range
                if len(match.groups()) >= 2 and match.group(2):
                    amount_from = int(match.group(1).replace(' ', ''))
                    amount_to = int(match.group(2).replace(' ', ''))
                    
                    if 'тыс' in match.group(0) or '000' in match.group(0):
                        amount_from = amount_from * 1000
                        amount_to = amount_to * 1000
                    
                    return f"{amount_from:,} - {amount_to:,} ₽".replace(',', ' ')
                else:
                    amount = int(match.group(1).replace(' ', '')) * 1000
                    return f"{amount:,} ₽".replace(',', ' ')
            except Exception as e:
                print(f"Error: {e}")
                pass
    return None

url = "https://shtrafy-gibdd.ru/koap/12-7-1"

print("="*80)
print("Testing Article 12.7")
print("="*80)

try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    full_text = soup.get_text()
    
    # Save for inspection
    with open('article_12_7_text.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"✅ Fetched successfully")
    print(f"📄 Content length: {len(full_text)} bytes\n")
    
    # Extract fine
    fine = extract_fine(full_text)
    
    if fine:
        print(f"💰 Fine extracted: {fine}")
    else:
        print(f"❌ Fine not found")
        
        # Debug: show what we're searching in
        print("\n🔍 Searching for patterns in text...")
        if 'от 5 до 15' in full_text:
            print("   ✅ Found 'от 5 до 15'")
            # Find context
            pos = full_text.find('от 5 до 15')
            print(f"   Context: ...{full_text[max(0,pos-50):pos+100]}...")
        
        if 'тыс' in full_text:
            print("   ✅ Found 'тыс'")
        
        if 'штраф' in full_text.lower():
            print("   ✅ Found 'штраф'")
    
    print("\n✅ Test complete")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
