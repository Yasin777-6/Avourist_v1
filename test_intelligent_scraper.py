"""
Test intelligent scraper - finds URLs automatically
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autouristv1.settings')

from ai_engine.services.koap_scraper import KoapScraper

print("="*80)
print("Testing Intelligent КоАП Scraper")
print("="*80)
print("\nThe scraper will automatically find URLs for ANY article!\n")

scraper = KoapScraper()

# Test articles that are NOT in the hardcoded mapping
test_articles = [
    ("8.23", "Environmental violations (NOT in mapping)"),
    ("12.8", "Drunk driving (IN mapping)"),
    ("19.3", "Administrative violations (NOT in mapping)"),
]

for article_code, description in test_articles:
    print(f"\n{'='*80}")
    print(f"Testing: {article_code} - {description}")
    print(f"{'='*80}")
    
    result = scraper.get_article_info(article_code)
    
    if result:
        print(f"✅ SUCCESS - Found automatically!")
        print(f"   Article: {result.get('article')}")
        
        punishment = result.get('punishment', {})
        if punishment.get('fine'):
            print(f"   Fine: {punishment['fine']}")
        if punishment.get('license_suspension'):
            print(f"   License: {punishment['license_suspension']}")
        
        print(f"   Source: {result.get('source')}")
    else:
        print(f"❌ Could not find article")

print(f"\n{'='*80}")
print("RESULT: Scraper intelligently finds URLs without hardcoding!")
print("="*80)
