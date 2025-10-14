"""
Knowledge Base Loader
Loads КоАП articles and petition templates for agents
Uses koap_fines_complete.json (128 articles) scraped from https://shtrafy-gibdd.ru/koap
Dynamically fetches current penalties from shtrafy-gibdd.ru when needed
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Knowledge base for legal data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.koap_articles = self._load_koap_articles()
        self.koap_fines_complete = self._load_koap_fines_complete()
        self.petition_templates = self._load_petition_templates()
        self.scraper = None  # Lazy load scraper
        logger.info(f"Loaded {len(self.koap_articles)} КоАП articles, {len(self.koap_fines_complete)} complete fines, and {len(self.petition_templates)} petition templates")
    
    def _load_koap_articles(self) -> List[Dict]:
        """Load КоАП articles from JSON"""
        try:
            file_path = self.data_dir / 'koap_articles.json'
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('articles', [])
        except Exception as e:
            logger.error(f"Failed to load КоАП articles: {e}")
            return []
    
    def _load_koap_fines_complete(self) -> Dict:
        """Load complete КоАП fines database from koap_fines_complete.json (scraped from shtrafy-gibdd.ru/koap)"""
        try:
            # Load from root directory
            file_path = self.data_dir.parent.parent / 'koap_fines_complete.json'
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded complete fines database from {file_path} - Source: {data.get('source', 'unknown')}")
                return data.get('articles', {})
        except Exception as e:
            logger.error(f"Failed to load КоАП fines complete: {e}")
            return {}
    
    def _load_petition_templates(self) -> List[Dict]:
        """Load petition templates from JSON"""
        try:
            file_path = self.data_dir / 'petition_templates.json'
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('templates', [])
        except Exception as e:
            logger.error(f"Failed to load petition templates: {e}")
            return []
    
    def find_article_by_keywords(self, text: str) -> Optional[Dict]:
        """
        Find КоАП article by keywords in text
        Returns article with highest keyword match
        """
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        for article in self.koap_articles:
            score = 0
            keywords = article.get('keywords', [])
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = article
        
        if best_match:
            logger.info(f"Found article {best_match['article']} with score {best_score}")
        
        return best_match
    
    def get_article_by_code(self, article_code: str) -> Optional[Dict]:
        """
        Get article by exact code (e.g., 'ч.1 ст.12.8 КоАП РФ')
        First checks local cache, then complete fines database, then scrapes from shtrafy-gibdd.ru if needed
        """
        # Try local cache first
        for article in self.koap_articles:
            if article['article'] == article_code:
                logger.info(f"Found article {article_code} in local cache")
                return article
        
        # Try complete fines database
        fine_info = self.get_fine_from_complete_db(article_code)
        if fine_info:
            logger.info(f"Found article {article_code} in complete fines database")
            return fine_info
        
        # If not found, try scraping from shtrafy-gibdd.ru
        logger.info(f"Article {article_code} not in cache, attempting to scrape...")
        scraped_article = self._scrape_article(article_code)
        
        if scraped_article:
            # Add to cache for future use
            self.koap_articles.append(scraped_article)
            logger.info(f"Successfully scraped and cached article {article_code}")
            return scraped_article
        
        return None
    
    def get_fine_from_complete_db(self, article_code: str) -> Optional[Dict]:
        """
        Get fine information from koap_fines_complete.json
        Converts article code like 'ч.1 ст.12.8 КоАП РФ' to '12.8ч.1'
        Source: https://shtrafy-gibdd.ru/koap
        """
        # Extract article number from code
        # Example: 'ч.1 ст.12.8 КоАП РФ' -> '12.8ч.1'
        import re
        match = re.search(r'ч\.(\d+)\s+ст\.(\d+\.\d+)', article_code)
        if match:
            part = match.group(1)
            article_num = match.group(2)
            key = f"{article_num}ч.{part}"
        else:
            # Try without part number: 'ст.12.8 КоАП РФ' -> '12.8'
            match = re.search(r'ст\.(\d+\.\d+)', article_code)
            if match:
                key = match.group(1)
            else:
                return None
        
        # Look up in complete database
        if key in self.koap_fines_complete:
            fine_data = self.koap_fines_complete[key]
            # Convert to standard format
            return {
                'article': article_code,
                'title': fine_data.get('description', ''),
                'punishment': {
                    'fine': fine_data.get('fine', ''),
                    'details': fine_data.get('punishment', '')
                },
                'sources': ['https://shtrafy-gibdd.ru/koap'],
                'verified': True,
                'last_updated': '2025-10-14'
            }
        
        return None
    
    def _scrape_article(self, article_code: str) -> Optional[Dict]:
        """Scrape article from shtrafy-gibdd.ru/koap"""
        try:
            # Lazy load scraper
            if self.scraper is None:
                from ai_engine.services.koap_scraper import get_koap_scraper
                self.scraper = get_koap_scraper()
            
            return self.scraper.get_article_info(article_code)
        except Exception as e:
            logger.error(f"Failed to scrape article {article_code}: {e}")
            return None
    
    def get_petition_template(self, petition_type: str) -> Optional[Dict]:
        """Get petition template by type"""
        for template in self.petition_templates:
            if template['type'] == petition_type:
                return template
        return None
    
    def search_articles(self, query: str) -> List[Dict]:
        """
        Search articles by query
        Returns list of matching articles sorted by relevance
        """
        query_lower = query.lower()
        results = []
        
        for article in self.koap_articles:
            score = 0
            
            # Check title
            if query_lower in article.get('title', '').lower():
                score += 3
            
            # Check keywords
            for keyword in article.get('keywords', []):
                if keyword.lower() in query_lower:
                    score += 2
            
            # Check full text
            if query_lower in article.get('full_text', '').lower():
                score += 1
            
            if score > 0:
                results.append((score, article))
        
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [article for score, article in results]
    
    def get_article_info_for_prompt(self, article_code: str) -> str:
        """
        Get formatted article information for AI prompt
        """
        article = self.get_article_by_code(article_code)
        if not article:
            return f"Статья {article_code}"
        
        info = f"""
📋 {article['article']}
{article['title']}

Наказание:
{self._format_punishment(article.get('punishment', {}))}

Основания для обжалования:
{self._format_list(article.get('appeal_grounds', []))}

Шансы на успех: {article.get('success_probability', 'не определены')}
"""
        return info.strip()
    
    def _format_punishment(self, punishment: Dict) -> str:
        """Format punishment dict to string"""
        parts = []
        if punishment.get('fine'):
            parts.append(f"• Штраф: {punishment['fine']}")
        if punishment.get('license_suspension'):
            parts.append(f"• Лишение прав: {punishment['license_suspension']}")
        if punishment.get('criminal'):
            parts.append(f"• Уголовное наказание: {punishment['criminal']}")
        if punishment.get('additional'):
            parts.append(f"• Дополнительно: {punishment['additional']}")
        return '\n'.join(parts) if parts else "Не указано"
    
    def _format_list(self, items: List[str]) -> str:
        """Format list to numbered string"""
        return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))


# Global knowledge base instance
_kb_instance = None

def get_knowledge_base() -> KnowledgeBase:
    """Get global knowledge base instance (singleton)"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
