import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Test the actual website
r = requests.get('https://avtourist.info/vyigrannye-dela')
soup = BeautifulSoup(r.text, 'html.parser')

# Find first 3 thumbnail links
img_links = soup.find_all('a', class_='thumbnail')[:3]

for i, img_link in enumerate(img_links, 1):
    print(f"\n=== Image {i} ===")
    
    # Get the href (link to full image)
    href = img_link.get('href', '')
    print(f"Link href: {href}")
    
    # Get the img src (thumbnail)
    img = img_link.find('img')
    if img:
        src = img.get('src', '')
        print(f"Thumbnail src: {src}")
    
    # Try to access the full image via href
    if href:
        full_url = f"https://avtourist.info{href}"
        print(f"Full URL: {full_url}")
        
        try:
            # Encode the URL
            parts = full_url.rsplit('/', 1)
            if len(parts) == 2:
                base, filename = parts
                encoded_url = f"{base}/{quote(filename)}"
                print(f"Encoded URL: {encoded_url}")
                
                resp = requests.get(encoded_url, timeout=10)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"Size: {len(resp.content)} bytes")
                    print(f"Content-Type: {resp.headers.get('Content-Type')}")
        except Exception as e:
            print(f"Error: {e}")
