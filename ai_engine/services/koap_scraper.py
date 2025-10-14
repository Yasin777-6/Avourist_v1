"""
КоАП РФ Web Scraper
Dynamically fetches current penalties from consultant.ru
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re

logger = logging.getLogger(__name__)


class KoapScraper:
    """Scrapes КоАП РФ articles from shtrafy-gibdd.ru (specialized traffic fines site)"""
    
    # shtrafy-gibdd.ru - specialized traffic fines site with clear structure
    BASE_URL = "https://shtrafy-gibdd.ru/koap/"
    
    # Article mapping - add more as needed
    ARTICLE_URLS = {
        # Drunk driving & refusal
        "12.8": "12-8-1",    # Drunk driving
        "12.26": "12-26-1",  # Refusal to test
        
        # No license / documents
        "12.7": "12-7-1",    # Driving without license
        "12.3": "12-3",      # No documents
        
        # Speeding
        "12.9": "12-9-2",    # Speeding (various parts)
        
        # Traffic violations
        "12.15": "12-15",    # Wrong lane / oncoming traffic
        "12.12": "12-12",    # Running red light
        "12.13": "12-13",    # Intersection violations
        "12.14": "12-14",    # Maneuvering violations
        "12.16": "12-16",    # Road signs violations
        "12.18": "12-18",    # Pedestrian violations
        
        # Accidents
        "12.24": "12-24",    # Accident causing injury
        "12.27": "12-27",    # Leaving accident scene
        
        # equipment & registration
        "12.1": "12-1",      # Registration violations
        "12.2": "12-2",      # Unregistered vehicle
        "12.5": "12-5",      # equipment violations
        
        # Environmental violations (Chapter 8)
        "8.23": "8-23",      # Noise/emissions violations
        
        # Add more as needed - just find the URL slug on shtrafy-gibdd.ru
        # Works with ANY chapter: 8.x, 12.x, 19.x, etc.
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Load article mappings from file if available
        self._load_article_mappings()
    
    def _load_article_mappings(self):
        """Load article URL mappings from JSON file if available"""
        try:
            import json
            from pathlib import Path
            
            # Try to load from project root
            mapping_file = Path(__file__).parent.parent.parent / 'koap_articles_map.json'
            
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Merge with existing mappings
                for article_num, info in data.get('articles', {}).items():
                    if article_num not in self.ARTICLE_URLS:
                        self.ARTICLE_URLS[article_num] = info['url_slug']
                
                logger.info(f"Loaded {len(data.get('articles', {}))} article mappings from file")
        except Exception as e:
            logger.debug(f"Could not load article mappings: {e}")
    
    def get_article_info(self, article_code: str) -> Optional[Dict]:
        """
        Fetch article information from shtrafy-gibdd.ru
        Intelligently tries multiple URL patterns
        
        Args:
            article_code: Article code like "ч.1 ст.12.8" or "12.8" or "8.23"
            
        Returns:
            Dict with article info or None if not found
        """
        try:
            # Extract article number from code
            article_num = self._extract_article_number(article_code)
            if not article_num:
                logger.error(f"Could not extract article number from: {article_code}")
                return None
            
            # Try multiple URL patterns intelligently
            url_slug = self._find_article_url(article_num)
            if not url_slug:
                logger.warning(f"Could not determine URL for article {article_num}")
                return None
            
            # Fetch the page
            url = f"{self.BASE_URL}{url_slug}"
            logger.info(f"Fetching КоАП article from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            full_text = soup.get_text()
            
            # Parse article content
            article_data = self._parse_shtrafy_gibdd(full_text, article_num)
            
            if article_data:
                logger.info(f"Successfully scraped article {article_code}")
                return article_data
            else:
                logger.warning(f"Article {article_code} not found on page")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping article {article_code}: {e}")
            return None
    
    def _find_article_url(self, article_num: str) -> Optional[str]:
        """
        Intelligently find the URL for an article
        Tries known mappings first, then tries common patterns
        """
        # First check if we have it in our mapping
        if article_num in self.ARTICLE_URLS:
            return self.ARTICLE_URLS[article_num]
        
        # Try common URL patterns
        # Pattern 1: Simple dash (12.8 -> 12-8)
        simple_slug = article_num.replace('.', '-')
        
        # Pattern 2: With part 1 (12.8 -> 12-8-1)
        part1_slug = f"{simple_slug}-1"
        
        # Pattern 3: With part 2 (12.9 -> 12-9-2)
        part2_slug = f"{simple_slug}-2"
        
        # Try each pattern
        for slug in [part1_slug, simple_slug, part2_slug]:
            try:
                test_url = f"{self.BASE_URL}{slug}"
                response = self.session.head(test_url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"Found article {article_num} at: {slug}")
                    # Cache it for next time
                    self.ARTICLE_URLS[article_num] = slug
                    return slug
            except:
                continue
        
        logger.warning(f"Could not find URL pattern for article {article_num}")
        return None
    
    def _extract_article_number(self, article_code: str) -> Optional[str]:
        """Extract article number like '12.8' from various formats"""
        # Try to match patterns like "ч.1 ст.12.8", "12.8", "ст.12.8"
        patterns = [
            r'ст\.(\d+\.\d+)',  # ст.12.8
            r'(\d+\.\d+)',       # 12.8
        ]
        
        for pattern in patterns:
            match = re.search(pattern, article_code)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_shtrafy_gibdd(self, full_text: str, article_num: str) -> Optional[Dict]:
        """
        Parse article content from shtrafy-gibdd.ru text
        
        Example text: "45 000 руб. и лишение прав сроком от 1,5 до 2 лет"
        """
        try:
            # Extract title
            title_match = re.search(rf'Статья {article_num}[^\n]*([^\n]+)', full_text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else f"Статья {article_num}"
            
            # Extract fine and license suspension
            fine = self._extract_fine(full_text)
            license_suspension = self._extract_license_suspension(full_text)
            
            if not fine and not license_suspension:
                logger.warning(f"Could not extract punishment info for article {article_num}")
                return None
            
            return {
                'article': f'ст.{article_num} КоАП РФ',
                'title': title,
                'punishment': {
                    'fine': fine or 'штраф',
                    'license_suspension': license_suspension or 'лишение прав'
                },
                'source': f'{self.BASE_URL}{self.ARTICLE_URLS.get(article_num, article_num)}',
                'scraped': True
            }
            
        except Exception as e:
            logger.error(f"Error parsing article {article_num}: {e}")
            return None
    
    def _extract_fine(self, text: str) -> Optional[str]:
        """Extract fine amount from text"""
        # Look for patterns like "45 000 руб", "от 5 до 15 тыс. руб", "500 рублей"
        patterns = [
            # Range patterns (e.g., "от 5 до 15 тыс. руб")
            r'от\s*(\d+)\s*до\s*(\d+)\s*тыс',  # "от 5 до 15 тыс"
            r'от\s*(\d+)\s*до\s*(\d+)\s*000',  # "от 5 до 15 000"
            r'от\s*(\d+[\s\d]+)\s*до\s*(\d+[\s\d]+)\s*руб',  # "от 5 000 до 15 000 руб"
            
            # Large amounts (thousands)
            r'(\d+)\s*000\s*руб',  # "45 000 руб"
            r'(\d+)\s*тысяч',  # "45 тысяч"
            r'штраф[^\d]*(\d+)\s*000',  # "штраф 45 000"
            
            # Small amounts (hundreds) - must come after large amounts
            r'штраф[^\d]*(\d+)\s*рублей',  # "штраф 500 рублей"
            r'(\d{3,4})\s*рублей',  # "500 рублей" or "1500 рублей"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Check if it's a range (2 groups)
                    if len(match.groups()) >= 2 and match.group(2):
                        amount_from = int(match.group(1).replace(' ', ''))
                        amount_to = int(match.group(2).replace(' ', ''))
                        
                        # Multiply by 1000 if "тыс" or "000" in match
                        if 'тыс' in match.group(0).lower() or '000' in match.group(0):
                            amount_from = amount_from * 1000
                            amount_to = amount_to * 1000
                        
                        return f"{amount_from:,} - {amount_to:,} ₽".replace(',', ' ')
                    else:
                        # Single amount
                        amount_str = match.group(1).replace(' ', '')
                        amount = int(amount_str)
                        
                        # Only multiply if it's in thousands
                        matched_text = match.group(0).lower()
                        if 'тысяч' in matched_text or 'тыс' in matched_text:
                            amount = amount * 1000
                        elif '000' in matched_text and 'рублей' not in matched_text:
                            # "45 000 руб" but not "500 рублей"
                            amount = amount * 1000
                        
                        return f"{amount:,} ₽".replace(',', ' ')
                except Exception as e:
                    logger.debug(f"Error parsing fine amount: {e}")
                    pass
        
        return None
    
    def _extract_license_suspension(self, text: str) -> Optional[str]:
        """Extract license suspension period from text"""
        # Look for patterns like "лишение прав сроком от 1,5 до 2 лет"
        patterns = [
            r'от\s*(\d+[,\.]?\d*)\s*до\s*(\d+)\s*лет',  # "от 1,5 до 2 лет"
            r'от\s*(\d+[,\.]?\d*)\s*до\s*(\d+)\s*года',  # "от 1,5 до 2 года"
            r'от\s*(\d+)\s*до\s*(\d+)\s*месяцев',  # "от 4 до 6 месяцев"
            r'лишение прав сроком от\s*(\d+[,\.]?\d*)\s*до\s*(\d+[,\.]?\d*)\s*(лет|года|месяцев)',
            r'лишение права управления.*?от\s*(\d+[,\.]?\d*)\s*до\s*(\d+[,\.]?\d*)\s*(лет|года|месяцев)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                period_from = match.group(1).replace(',', '.')
                period_to = match.group(2).replace(',', '.')
                
                # Check if pattern has explicit period type
                if len(match.groups()) >= 3:
                    period_type = match.group(3)
                    if 'месяц' in period_type:
                        return f"{period_from}-{period_to} месяцев"
                    else:
                        return f"{period_from}-{period_to} года"
                else:
                    # Infer from context
                    if 'месяц' in match.group(0):
                        return f"{period_from}-{period_to} месяцев"
                    else:
                        return f"{period_from}-{period_to} года"
        
        return None


# Global scraper instance
_scraper_instance = None

def get_koap_scraper() -> KoapScraper:
    """Get global scraper instance (singleton)"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = KoapScraper()
    return _scraper_instance
