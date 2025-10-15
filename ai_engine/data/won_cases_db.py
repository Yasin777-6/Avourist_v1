"""
Won Cases Database - Provides access to won cases data
"""

import logging
import json
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


class WonCasesDB:
    """Database for won cases"""
    
    def __init__(self):
        self.data_file = Path(__file__).parent / 'won_cases.json'
        self.cases = self._load_cases()
    
    def _load_cases(self) -> List[Dict]:
        """Load cases from JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    cases = json.load(f)
                logger.info(f"Loaded {len(cases)} won cases from database")
                return cases
        except Exception as e:
            logger.error(f"Error loading won cases: {e}")
        
        # Return default cases if file doesn't exist
        return self._get_default_cases()
    
    def _get_default_cases(self) -> List[Dict]:
        """Get default won cases (fallback)"""
        return [
            {
                "title": "Отмена лишения прав по ч.1 ст.12.8 КоАП РФ",
                "article": "12.8",
                "result": "Постановление отменено, права сохранены",
                "key_arguments": "Отсутствие понятых при освидетельствовании; Нарушение процедуры освидетельствования; Прибор без актуальной поверки",
                "description": "Клиент был задержан за управление в состоянии опьянения. Мы нашли процессуальные нарушения: отсутствие понятых и нарушение процедуры. Результат: постановление отменено."
            },
            {
                "title": "Снижение наказания с лишения прав на штраф",
                "article": "12.8",
                "result": "Вместо лишения прав — штраф 30,000₽",
                "key_arguments": "Смягчающие обстоятельства; Первое нарушение; Нарушения в протоколе",
                "description": "Клиент впервые нарушил ПДД, есть смягчающие обстоятельства. Мы нашли нарушения в протоколе. Результат: вместо лишения прав получили штраф."
            },
            {
                "title": "Отмена постановления по ст.12.26 КоАП РФ",
                "article": "12.26",
                "result": "Постановление отменено",
                "key_arguments": "Незаконное требование освидетельствования; Отсутствие оснований; Нарушение прав",
                "description": "Инспектор незаконно требовал пройти освидетельствование без оснований. Мы доказали нарушение прав клиента. Результат: постановление отменено."
            },
            {
                "title": "Оправдание по ст.12.9 КоАП РФ (превышение скорости)",
                "article": "12.9",
                "result": "Оправдан, штраф отменен",
                "key_arguments": "Ошибка радара; Отсутствие поверки прибора; Нарушения в протоколе",
                "description": "Клиент обвинялся в превышении скорости. Мы доказали, что радар был без поверки и дал ошибочные показания. Результат: оправдан."
            },
            {
                "title": "Возврат прав досрочно",
                "article": "12.8",
                "result": "Права возвращены досрочно",
                "key_arguments": "Безупречное поведение; Положительные характеристики; Необходимость управления ТС",
                "description": "Клиент был лишен прав, но мы добились досрочного возврата через суд на основании безупречного поведения и необходимости управления ТС для работы."
            }
        ]
    
    def get_by_article(self, article: str) -> List[Dict]:
        """Get won cases by article number"""
        matching_cases = [
            case for case in self.cases 
            if case.get('article') == article
        ]
        
        if not matching_cases:
            # Return similar cases if exact match not found
            article_base = article.split('.')[0]  # e.g., "12" from "12.8"
            matching_cases = [
                case for case in self.cases 
                if case.get('article', '').startswith(article_base)
            ]
        
        return matching_cases[:5]  # Return top 5
    
    def get_all(self) -> List[Dict]:
        """Get all won cases"""
        return self.cases


# Singleton instance
_won_cases_db = None


def get_won_cases_db() -> WonCasesDB:
    """Get won cases database instance"""
    global _won_cases_db
    if _won_cases_db is None:
        _won_cases_db = WonCasesDB()
    return _won_cases_db


def get_won_cases_by_article(article: str) -> List[Dict]:
    """Utility function to get won cases by article"""
    db = get_won_cases_db()
    return db.get_by_article(article)
