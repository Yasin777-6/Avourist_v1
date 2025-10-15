import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Check an individual case page
url = 'https://avtourist.info/vyigrannye-dela/item/2757-delo-po-st-12-8-1-prekrashcheno'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

# Find all images
all_imgs = soup.find_all('img')
print(f"Found {len(all_imgs)} images on the page\n")

# Look for delo images
delo_imgs = [img for img in all_imgs if 'delo' in img.get('src', '')]
print(f"Found {len(delo_imgs)} delo images\n")

for i, img in enumerate(delo_imgs[:3], 1):
    src = img.get('src', '')
    print(f"Image {i}: {src}")
    
    # Try to get full size
    full_url = src.replace('/thumbnails', '').replace('-fill-200x300', '')
    print(f"  Trying full: {full_url}")
    
    # Test it
    parts = full_url.rsplit('/', 1)
    if len(parts) == 2:
        base, filename = parts
        test_url = f"https://avtourist.info{base}/{quote(filename)}"
        try:
            resp = requests.get(test_url, timeout=5)
            print(f"  Status: {resp.status_code}, Size: {len(resp.content) if resp.status_code == 200 else 'N/A'}")
        except Exception as e:
            print(f"  Error: {e}")
    print()
