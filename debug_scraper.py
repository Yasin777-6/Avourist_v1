"""
Debug scraper - saves HTML and shows article text
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.consultant.ru/document/cons_doc_LAW_34661/"

print("Fetching page...")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)

soup = BeautifulSoup(response.text, 'html.parser')
full_text = soup.get_text()

# Find article 12.8
pos = full_text.find('Статья 12.8')
if pos != -1:
    print(f"\n✅ Found 'Статья 12.8' at position {pos}\n")
    print("="*80)
    print("ARTICLE TEXT (next 1500 characters):")
    print("="*80)
    article_text = full_text[pos:pos+3000]
    
    # Save to file
    with open('article_12_8_text.txt', 'w', encoding='utf-8') as f:
        f.write(article_text)
    print("Saved to article_12_8_text.txt")
    
    print(article_text)
    
    # Also try to find specific keywords
    print("\n" + "="*80)
    print("SEARCHING FOR KEYWORDS:")
    print("="*80)
    if 'тысяч рублей' in article_text:
        print("✅ Found 'тысяч рублей'")
    if 'штраф' in article_text:
        print("✅ Found 'штраф'")
    if 'лишение' in article_text:
        print("✅ Found 'лишение'")
    if 'права управления' in article_text:
        print("✅ Found 'права управления'")
    print("="*80)
else:
    print("❌ Not found")
    print("\nSearching for '12.8' anywhere...")
    pos = full_text.find('12.8')
    if pos != -1:
        print(f"Found '12.8' at position {pos}")
        print(full_text[max(0, pos-200):pos+500])
