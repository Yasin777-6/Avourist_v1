"""
Simple test for КоАП scraper (no Django dependencies)
"""
import requests
from bs4 import BeautifulSoup
import re


def test_scrape_article(article_num="12.8"):
    """Test scraping a specific article"""
    print(f"\n{'='*60}")
    print(f"Testing КоАП Scraper for Article {article_num}")
    print(f"{'='*60}\n")
    
    url = "https://www.consultant.ru/document/cons_doc_LAW_34661/"
    
    try:
        print(f"📡 Fetching from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Response received: {response.status_code}")
        print(f"📄 Content length: {len(response.text)} bytes\n")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for article in full text
        print(f"🔍 Searching for article {article_num}...")
        
        full_text = soup.get_text()
        
        # Find article position
        article_patterns = [
            f'Статья {article_num}.',
            f'Статья {article_num} ',
            f'ст. {article_num}',
            f'ст.{article_num}',
        ]
        
        article_pos = -1
        for pattern in article_patterns:
            article_pos = full_text.find(pattern)
            if article_pos != -1:
                print(f"✅ Found article at position {article_pos}")
                break
        
        if article_pos == -1:
            print(f"❌ Article {article_num} not found in page")
            print(f"\n📝 Sample content (first 1000 chars):")
            print(full_text[:1000])
            return
        
        # Extract text around article (next 2000 chars should contain punishment)
        article_section = full_text[article_pos:article_pos + 2000]
        
        print(f"\n📋 Article section found:")
        print("-" * 60)
        print(article_section[:500])
        print("-" * 60)
        
        # Extract fine with better patterns
        print(f"\n💰 Extracting fine...")
        fine_patterns = [
            r'штраф.*?в размере.*?(\d+)\s*тысяч',
            r'штраф.*?(\d+)\s*тысяч.*?рублей',
            r'административный штраф.*?(\d+)\s*тысяч',
            r'наложение административного штрафа.*?(\d+)\s*тысяч',
            r'штраф.*?(\d{2,6})\s*рублей',
        ]
        
        fine_found = False
        for pattern in fine_patterns:
            match = re.search(pattern, article_section, re.IGNORECASE | re.DOTALL)
            if match:
                amount_str = match.group(1).replace(' ', '')
                try:
                    amount = int(amount_str)
                    # If it's in thousands, multiply
                    if 'тысяч' in match.group(0).lower():
                        amount = amount * 1000
                    print(f"   ✅ Fine: {amount:,} ₽".replace(',', ' '))
                    fine_found = True
                    break
                except:
                    pass
        
        if not fine_found:
            print(f"   ❌ Could not extract fine amount")
        
        # Extract license suspension
        print(f"\n🚫 Extracting license suspension...")
        license_patterns = [
            r'лишение права управления.*?на срок.*?от\s*(\d+\.?\d*)\s*до\s*(\d+\.?\d*)\s*(лет|года|месяцев)',
            r'лишение права управления.*?(\d+\.?\d*)\s*до\s*(\d+\.?\d*)\s*(лет|года|месяцев)',
            r'лишением права управления.*?от\s*(\d+\.?\d*)\s*до\s*(\d+\.?\d*)\s*(лет|года|месяцев)',
        ]
        
        license_found = False
        for pattern in license_patterns:
            match = re.search(pattern, article_section, re.IGNORECASE | re.DOTALL)
            if match:
                period_from = match.group(1)
                period_to = match.group(2)
                period_type = match.group(3)
                print(f"   ✅ License suspension: {period_from} - {period_to} {period_type}")
                license_found = True
                break
        
        if not license_found:
            print(f"   ❌ Could not extract license suspension period")
        
    except requests.Timeout:
        print(f"❌ Request timed out after 10 seconds")
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_articles():
    """Test multiple articles"""
    articles = ["12.8", "12.26", "12.9", "12.15"]
    
    for article in articles:
        test_scrape_article(article)
        print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    print("\n🚀 КоАП Scraper Simple Test\n")
    print("This test will attempt to scrape penalties from consultant.ru")
    print("Make sure you have internet connection!\n")
    
    # Test single article first
    test_scrape_article("12.8")
    
    # Uncomment to test multiple articles
    # test_multiple_articles()
    
    print("\n✅ Test completed!\n")
