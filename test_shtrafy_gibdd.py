"""
Test scraping from shtrafy-gibdd.ru (specialized traffic fines site)
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://shtrafy-gibdd.ru/koap/12-8-1"

print("="*80)
print("Testing shtrafy-gibdd.ru")
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
    
    # Get text
    full_text = soup.get_text()
    
    print("="*80)
    print("PAGE CONTENT (first 2000 chars):")
    print("="*80)
    print(full_text[:2000])
    print("="*80)
    
    # Save full text
    with open('shtrafy_gibdd_12_8.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)
    print("\n💾 Saved full text to shtrafy_gibdd_12_8.txt")
    
    # Search for fine amount
    print("\n💰 Searching for fine amount...")
    fine_patterns = [
        r'(\d+)\s*000\s*₽',
        r'(\d+)\s*000\s*руб',
        r'(\d+)\s+тысяч',
        r'штраф.*?(\d+)\s*000',
        r'(\d+)\s*тыс',
    ]
    
    for pattern in fine_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            print(f"   Pattern '{pattern}' found: {matches}")
    
    # Search for license suspension
    print("\n🚫 Searching for license suspension...")
    license_patterns = [
        r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*(лет|года|месяц)',
        r'от\s+(\d+\.?\d*)\s+до\s+(\d+\.?\d*)\s+(лет|года|месяц)',
        r'лишение.*?(\d+\.?\d*)\s*-\s*(\d+\.?\d*)',
    ]
    
    for pattern in license_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            print(f"   Pattern '{pattern}' found: {matches}")
    
    # Look for specific keywords
    print("\n🔍 Keyword search:")
    keywords = ['штраф', 'лишение', 'права', '000', 'тысяч', 'рублей']
    for keyword in keywords:
        count = full_text.lower().count(keyword.lower())
        if count > 0:
            print(f"   '{keyword}': found {count} times")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed!\n")
