"""
Test script for КоАП scraper
Tests scraping from consultant.ru and knowledge base integration
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autouristv1.settings')
django.setup()

from ai_engine.services.koap_scraper import get_koap_scraper
from ai_engine.data.knowledge_base import get_knowledge_base


def test_scraper():
    """Test the КоАП scraper directly"""
    print("=" * 60)
    print("TEST 1: Direct Scraper Test")
    print("=" * 60)
    
    scraper = get_koap_scraper()
    
    # Test articles
    test_articles = [
        "ч.1 ст.12.8 КоАП РФ",
        "12.8",
        "ст.12.26",
    ]
    
    for article_code in test_articles:
        print(f"\n📋 Testing: {article_code}")
        print("-" * 60)
        
        result = scraper.get_article_info(article_code)
        
        if result:
            print(f"✅ Success!")
            print(f"   Article: {result.get('article', 'N/A')}")
            print(f"   Title: {result.get('title', 'N/A')[:80]}...")
            
            punishment = result.get('punishment', {})
            if punishment.get('fine'):
                print(f"   Fine: {punishment['fine']}")
            if punishment.get('license_suspension'):
                print(f"   License Suspension: {punishment['license_suspension']}")
            
            print(f"   Source: {result.get('source', 'N/A')}")
        else:
            print(f"❌ Failed to scrape article")


def test_knowledge_base():
    """Test knowledge base with scraper integration"""
    print("\n\n" + "=" * 60)
    print("TEST 2: Knowledge Base Integration Test")
    print("=" * 60)
    
    kb = get_knowledge_base()
    
    # Test articles
    test_articles = [
        "ч.1 ст.12.8 КоАП РФ",  # Should be in cache
        "ч.1 ст.12.26 КоАП РФ", # Should be in cache
        "ч.4 ст.12.15 КоАП РФ", # Might need scraping
    ]
    
    for article_code in test_articles:
        print(f"\n📋 Testing: {article_code}")
        print("-" * 60)
        
        article = kb.get_article_by_code(article_code)
        
        if article:
            print(f"✅ Found!")
            print(f"   Article: {article.get('article', 'N/A')}")
            
            punishment = article.get('punishment', {})
            if punishment.get('fine'):
                print(f"   Fine: {punishment['fine']}")
            if punishment.get('license_suspension'):
                print(f"   License Suspension: {punishment['license_suspension']}")
            
            if article.get('scraped'):
                print(f"   🌐 Scraped from web")
            else:
                print(f"   💾 From local cache")
        else:
            print(f"❌ Article not found")


def test_article_lookup():
    """Test article lookup by keywords"""
    print("\n\n" + "=" * 60)
    print("TEST 3: Article Lookup by Keywords")
    print("=" * 60)
    
    kb = get_knowledge_base()
    
    test_queries = [
        "пьяный за рулем",
        "отказ от медосвидетельствования",
        "превышение скорости",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 60)
        
        article = kb.find_article_by_keywords(query)
        
        if article:
            print(f"✅ Found: {article.get('article', 'N/A')}")
            print(f"   Title: {article.get('title', 'N/A')[:60]}...")
            
            punishment = article.get('punishment', {})
            if punishment.get('fine'):
                print(f"   Fine: {punishment['fine']}")
            if punishment.get('license_suspension'):
                print(f"   License: {punishment['license_suspension']}")
        else:
            print(f"❌ No article found")


def test_formatted_output():
    """Test formatted output for AI prompt"""
    print("\n\n" + "=" * 60)
    print("TEST 4: Formatted Output for AI")
    print("=" * 60)
    
    kb = get_knowledge_base()
    
    article_code = "ч.1 ст.12.8 КоАП РФ"
    print(f"\n📋 Article: {article_code}")
    print("-" * 60)
    
    formatted = kb.get_article_info_for_prompt(article_code)
    print(formatted)


if __name__ == "__main__":
    print("\n🚀 Starting КоАП Scraper Tests\n")
    
    try:
        # Run tests
        test_scraper()
        test_knowledge_base()
        test_article_lookup()
        test_formatted_output()
        
        print("\n\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nCheck the output above for any errors.")
        print("If scraping failed, check your internet connection.")
        print("Cached articles should still work even without internet.\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
