"""
Won Cases Scraper - Scrapes won cases from avtourist.info
"""

import logging
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re
import os
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class WonCasesScraper:
    """Scraper for won cases from avtourist.info"""
    
    def __init__(self):
        self.base_url = "https://avtourist.info/vyigrannye-dela"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data_file = Path(__file__).parent / 'won_cases.json'
        self.images_dir = Path(__file__).parent / 'won_cases_images'
        self.images_dir.mkdir(exist_ok=True)
    
    def scrape_won_cases(self) -> list:
        """Scrape won cases from the website"""
        try:
            logger.info(f"Scraping won cases from {self.base_url}")
            
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            cases = []
            
            # First, find all document images from the header section
            header_images = self._scrape_header_images(soup)
            logger.info(f"Found {len(header_images)} document images in header")
            
            # Find all h3 headers with links (case titles)
            case_headers = soup.find_all('h3')
            
            for header in case_headers:
                try:
                    link = header.find('a')
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    # Skip if no title
                    if not title or len(title) < 10:
                        continue
                    
                    # Extract article from title or URL
                    article = self._extract_article(title)
                    
                    # Find category (next sibling or parent)
                    category = ""
                    category_link = header.find_next('a', href=re.compile(r'/category/'))
                    if category_link:
                        category = category_link.get_text(strip=True).replace('(Категория - ', '').replace(')', '')
                    
                    # Get document images for this article from header images
                    images = []
                    if article and article in header_images:
                        images = header_images[article][:3]  # Take first 3 images
                    
                    case = {
                        'title': title,
                        'url': url if url.startswith('http') else f"https://avtourist.info{url}",
                        'article': article,
                        'category': category,
                        'result': 'Положительное решение',
                        'key_arguments': self._extract_arguments_from_title(title),
                        'description': title,
                        'images': images,  # List of image URLs
                        'image_count': len(images)
                    }
                    
                    cases.append(case)
                    
                except Exception as e:
                    logger.error(f"Error parsing case header: {e}")
                    continue
            
            logger.info(f"Scraped {len(cases)} won cases")
            
            # Save to JSON file
            self._save_cases(cases)
            
            return cases
            
        except Exception as e:
            logger.error(f"Error scraping won cases: {e}")
            logger.exception("Full traceback:")
            return []
    
    def _extract_article(self, text: str) -> str:
        """Extract article number from text"""
        # Look for patterns like "12.8", "12.26", "ст. 12.8"
        article_match = re.search(r'(?:ст\.\s*)?(\d+\.\d+)', text)
        if article_match:
            return article_match.group(1)
        
        # Look for patterns like "12.8.1"
        article_match = re.search(r'(\d+\.\d+\.\d+)', text)
        if article_match:
            return article_match.group(1)
        
        return ""
    
    def _extract_arguments_from_title(self, title: str) -> str:
        """Extract key arguments from case title"""
        # Common argument patterns
        arguments = []
        
        if 'процессуальн' in title.lower():
            arguments.append('Процессуальные нарушения')
        if 'понят' in title.lower():
            arguments.append('Отсутствие понятых')
        if 'прав' in title.lower() and 'разъясн' in title.lower():
            arguments.append('Не разъяснены права')
        if 'освидетельствован' in title.lower():
            arguments.append('Нарушения при освидетельствовании')
        if 'протокол' in title.lower():
            arguments.append('Нарушения в протоколе')
        if 'доказательств' in title.lower():
            arguments.append('Недопустимые доказательства')
        if 'состав' in title.lower() and 'отсутств' in title.lower():
            arguments.append('Отсутствие состава правонарушения')
        
        return '; '.join(arguments) if arguments else 'Процессуальные нарушения'
    
    def _scrape_header_images(self, soup) -> dict:
        """Scrape ALL document images from the page"""
        images_by_article = {}
        
        # Find ALL images with class "thumbnail" and "magnific-popup"
        # These are the court document images
        img_links = soup.find_all('a', class_='thumbnail')
        
        logger.info(f"Found {len(img_links)} total image links")
        
        for link in img_links:
            img_tag = link.find('img')
            if img_tag:
                img_src = img_tag.get('src', '')
                img_alt = img_tag.get('alt', '')
                
                if img_src and 'delo' in img_src:
                    # Convert thumbnail to full image URL
                    # Change: /images/thumbnails/images/delo/file-fill-200x300.jpg
                    # To: /images/delo/file.jpg
                    full_img_url = img_src.replace('/images/thumbnails/images/delo/', '/images/delo/')
                    full_img_url = full_img_url.replace('-fill-200x300', '')
                    full_img_url = urljoin('https://avtourist.info', full_img_url)
                    
                    # Extract article from filename (e.g., "ст.12.8.1 дело..." or "12.8.1-spb...")
                    article = self._extract_article(img_alt)
                    if not article:
                        # Try extracting from src
                        article = self._extract_article(img_src)
                    
                    if article:
                        if article not in images_by_article:
                            images_by_article[article] = []
                        images_by_article[article].append({
                            'url': full_img_url,
                            'alt': img_alt,
                            'filename': os.path.basename(img_src)
                        })
        
        logger.info(f"Organized images into {len(images_by_article)} article groups")
        return images_by_article
    
    def _find_case_images(self, header_element) -> list:
        """Find document images near the case header"""
        images = []
        
        # Look for images in the main page (thumbnails)
        # Images are in <img> tags with src containing "/images/thumbnails/images/delo/"
        parent = header_element.find_parent(['div', 'section', 'article'])
        if parent:
            img_tags = parent.find_all('img', src=re.compile(r'/images/.*delo.*'))
            for img in img_tags[:3]:  # Take first 3 images
                img_src = img.get('src', '')
                if img_src:
                    # Convert thumbnail to full image
                    full_img_url = img_src.replace('/thumbnails', '').replace('-fill-200x300', '')
                    full_img_url = urljoin('https://avtourist.info', full_img_url)
                    images.append(full_img_url)
        
        return images
    
    def download_image(self, url: str, filename: str) -> str:
        """Download image from URL and save to local directory"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            filepath = self.images_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filename}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return ""
    
    def _parse_case_element(self, element) -> dict:
        """Parse a single case element"""
        case = {}
        
        # Extract title
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
        if title_elem:
            case['title'] = title_elem.get_text(strip=True)
        
        # Extract article number
        text = element.get_text()
        article_match = re.search(r'ст\.\s*(\d+\.?\d*)\s*КоАП', text)
        if article_match:
            case['article'] = article_match.group(1)
        
        # Extract result
        result_keywords = ['отменено', 'оправдан', 'выиграли', 'успех', 'права сохранены']
        for keyword in result_keywords:
            if keyword in text.lower():
                case['result'] = 'Положительное решение'
                break
        
        # Extract key arguments (look for bullet points or numbered lists)
        arguments = []
        list_items = element.find_all('li')
        for li in list_items[:3]:  # Take first 3 arguments
            arg_text = li.get_text(strip=True)
            if len(arg_text) > 10:  # Filter out short items
                arguments.append(arg_text)
        
        if arguments:
            case['key_arguments'] = '; '.join(arguments)
        
        # Extract description
        paragraphs = element.find_all('p')
        if paragraphs:
            description = ' '.join([p.get_text(strip=True) for p in paragraphs[:2]])
            case['description'] = description[:500]  # Limit length
        
        # Only return if we have minimum required fields
        if case.get('title') and case.get('article'):
            return case
        
        return None
    
    def _save_cases(self, cases: list):
        """Save cases to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(cases)} cases to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving cases: {e}")
    
    def load_cases(self) -> list:
        """Load cases from JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    cases = json.load(f)
                logger.info(f"Loaded {len(cases)} cases from {self.data_file}")
                return cases
        except Exception as e:
            logger.error(f"Error loading cases: {e}")
        return []


def scrape_and_save_won_cases():
    """Utility function to scrape and save won cases"""
    scraper = WonCasesScraper()
    cases = scraper.scrape_won_cases()
    return cases


if __name__ == '__main__':
    # Run scraper
    logging.basicConfig(level=logging.INFO)
    scrape_and_save_won_cases()
