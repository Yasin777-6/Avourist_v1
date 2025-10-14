"""
Final test of the updated КоАП scraper using shtrafy-gibdd.ru
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_engine.services.koap_scraper import get_koap_scraper

def test_scraper():
    """Test the scraper with real articles"""
    
    print("="*80)
    print("TESTING КоАП SCRAPER (shtrafy-gibdd.ru)")
    print("="*80)
    
    scraper = get_koap_scraper()
    
    # Test articles
    test_cases = [
        ("ч.1 ст.12.8 КоАП РФ", "Drunk driving"),
        ("12.8", "Drunk driving (short)"),
        ("ч.1 ст.12.26 КоАП РФ", "Refusal to take test"),
        ("12.26", "Refusal (short)"),
    ]
    
    for article_code, description in test_cases:
        print(f"\n{'='*80}")
        print(f"TEST: {article_code} - {description}")
        print(f"{'='*80}")
        
        result = scraper.get_article_info(article_code)
        
        if result:
            print(f"✅ SUCCESS!")
            print(f"\n📋 Article: {result.get('article')}")
            print(f"📝 Title: {result.get('title', 'N/A')[:80]}")
            
            punishment = result.get('punishment', {})
            if punishment.get('fine'):
                print(f"💰 Fine: {punishment['fine']}")
            if punishment.get('license_suspension'):
                print(f"🚫 License Suspension: {punishment['license_suspension']}")
            
            print(f"🔗 Source: {result.get('source')}")
            
            if result.get('scraped'):
                print(f"🌐 Scraped from web")
        else:
            print(f"❌ FAILED - Could not scrape article")
    
    print(f"\n{'='*80}")
    print("ALL TESTS COMPLETED")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    print("\n🚀 Starting Final Scraper Test\n")
    
    try:
        test_scraper()
        print("✅ All tests passed!\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
