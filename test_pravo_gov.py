"""
Test scraping from pravo.gov.ru (official government portal)
"""
import requests
from bs4 import BeautifulSoup
import re

def test_pravo_gov():
    """Test fetching КоАП from pravo.gov.ru"""
    
    # КоАП РФ document on pravo.gov.ru
    url = "http://pravo.gov.ru/proxy/ips/?docbody=&nd=102074277"
    
    print("="*80)
    print("Testing pravo.gov.ru (Official Government Legal Portal)")
    print("="*80)
    print(f"\n📡 Fetching: {url}\n")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Response: {response.status_code}")
        print(f"📄 Content length: {len(response.text)} bytes")
        print(f"📝 Encoding: {response.encoding}\n")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text()
        
        # Search for article 12.8
        print("🔍 Searching for 'Статья 12.8'...")
        
        pos = full_text.find('Статья 12.8')
        if pos == -1:
            pos = full_text.find('статья 12.8')
        if pos == -1:
            pos = full_text.find('12.8')
        
        if pos != -1:
            print(f"✅ Found at position {pos}\n")
            
            # Extract article section
            article_section = full_text[pos:pos+2000]
            
            print("="*80)
            print("ARTICLE 12.8 TEXT:")
            print("="*80)
            print(article_section[:1000])
            print("="*80)
            
            # Try to extract fine
            print("\n💰 Extracting fine amount...")
            fine_patterns = [
                r'(\d+)\s*тысяч рублей',
                r'штраф.*?(\d+)\s*тысяч',
                r'административный штраф.*?(\d+)\s*тысяч',
            ]
            
            for pattern in fine_patterns:
                match = re.search(pattern, article_section, re.IGNORECASE)
                if match:
                    amount = int(match.group(1)) * 1000
                    print(f"   ✅ Fine: {amount:,} ₽".replace(',', ' '))
                    break
            
            # Try to extract license suspension
            print("\n🚫 Extracting license suspension...")
            license_patterns = [
                r'лишение права управления.*?от\s*(\d+\.?\d*)\s*до\s*(\d+\.?\d*)\s*(лет|года)',
                r'лишением права управления.*?от\s*(\d+\.?\d*)\s*до\s*(\d+\.?\d*)\s*(лет|года)',
            ]
            
            for pattern in license_patterns:
                match = re.search(pattern, article_section, re.IGNORECASE)
                if match:
                    print(f"   ✅ License: {match.group(1)} - {match.group(2)} {match.group(3)}")
                    break
            
        else:
            print("❌ Article 12.8 not found")
            print("\n📝 Sample content (first 1000 chars):")
            print(full_text[:1000])
        
    except requests.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_alternative_sources():
    """Test alternative КоАП sources"""
    
    sources = [
        ("pravo.gov.ru", "http://pravo.gov.ru/proxy/ips/?docbody=&nd=102074277"),
        ("garant.ru", "https://base.garant.ru/12125267/"),
        ("kodeks.ru", "https://docs.cntd.ru/document/901807664"),
    ]
    
    print("\n\n" + "="*80)
    print("Testing Alternative Legal Sources")
    print("="*80)
    
    for name, url in sources:
        print(f"\n📡 Testing {name}...")
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            if response.status_code == 200:
                if '12.8' in response.text:
                    print(f"   ✅ {name}: Accessible, contains КоАП content")
                else:
                    print(f"   ⚠️  {name}: Accessible but КоАП not found")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:50]}")


if __name__ == "__main__":
    print("\n🚀 Testing Official Government Legal Portal\n")
    
    test_pravo_gov()
    test_alternative_sources()
    
    print("\n\n✅ Test completed!\n")
