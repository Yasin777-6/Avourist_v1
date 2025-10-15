import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Test the actual website
r = requests.get('https://avtourist.info/vyigrannye-dela')
soup = BeautifulSoup(r.text, 'html.parser')

# Find first 3 thumbnail images
imgs = soup.find_all('a', class_='thumbnail')[:3]

for i, img_link in enumerate(imgs, 1):
    img = img_link.find('img')
    if img:
        src = img.get('src', '')
        print(f"\nImage {i}:")
        print(f"  Original: {src}")
        
        # Test if original works
        test_url = f"https://avtourist.info{src}"
        try:
            resp = requests.get(test_url, timeout=5)
            print(f"  Original URL status: {resp.status_code}")
        except Exception as e:
            print(f"  Original URL error: {e}")
        
        # Try the href (full image)
        href = img_link.get('href', '')
        if href:
            print(f"  Full image href: {href}")
            try:
                resp = requests.get(f"https://avtourist.info{href}", timeout=5)
                print(f"  Full image status: {resp.status_code}")
            except Exception as e:
                print(f"  Full image error: {e}")
