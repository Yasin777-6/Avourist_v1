import requests
from bs4 import BeautifulSoup

# Test the actual website
r = requests.get('https://avtourist.info/vyigrannye-dela')
soup = BeautifulSoup(r.text, 'html.parser')

# Find first thumbnail link
img_link = soup.find('a', class_='thumbnail')

if img_link:
    print("=== Link Attributes ===")
    for attr, value in img_link.attrs.items():
        print(f"{attr}: {value}")
    
    print("\n=== Image Attributes ===")
    img = img_link.find('img')
    if img:
        for attr, value in img.attrs.items():
            print(f"{attr}: {value}")
    
    print("\n=== Trying to construct full image URL ===")
    img_src = img.get('src', '')
    print(f"Thumbnail: {img_src}")
    
    # Remove thumbnail-specific parts
    full_url = img_src.replace('/thumbnails', '').replace('-fill-200x300', '')
    print(f"Constructed full URL: https://avtourist.info{full_url}")
    
    # Test it
    from urllib.parse import quote
    parts = full_url.rsplit('/', 1)
    if len(parts) == 2:
        base, filename = parts
        encoded_url = f"https://avtourist.info{base}/{quote(filename)}"
        print(f"Encoded URL: {encoded_url}")
        
        try:
            resp = requests.get(encoded_url, timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Size: {len(resp.content)} bytes")
        except Exception as e:
            print(f"Error: {e}")
