"""
Case Analysis Agent - Shows Won Cases and Win Probability
Analyzes client's situation and shows relevant won cases from avtourist.info
"""

import logging
from typing import Dict, Any
from .base import BaseAgent
from ..prompts.case_analysis_prompt import CASE_ANALYSIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class CaseAnalysisAgent(BaseAgent):
    """
    Specialized agent for case analysis and showing won cases
    - Calculates win probability based on case details
    - Shows relevant won cases from database
    - Reduces client stress by showing success examples
    - Guides client toward signing contract
    """
    
    def __init__(self, deepseek_service, memory_service=None):
        super().__init__(deepseek_service, memory_service)
    
    def process(self, lead, message: str, context: Dict[str, Any]) -> str:
        """Process message for case analysis"""
        logger.info(f"CaseAnalysisAgent processing message for lead {lead.telegram_id}")
        
        # Add won cases to context if available
        won_cases = self._get_relevant_won_cases(lead)
        if won_cases:
            context['won_cases'] = won_cases
            logger.info(f"Found {len(won_cases)} relevant won cases")
        
        # Build messages for AI
        messages = self.build_messages(lead, message, context)
        
        # Call AI with higher temperature for empathetic responses
        response = self.call_ai(messages, temperature=0.7)
        
        logger.info(f"CaseAnalysisAgent response generated for lead {lead.telegram_id}")
        return response
    
    def get_system_prompt(self, lead, context: Dict[str, Any]) -> str:
        """Get case analysis system prompt with won cases context"""
        return CASE_ANALYSIS_SYSTEM_PROMPT(lead, context)
    
    def _get_relevant_won_cases(self, lead) -> list:
        """Get relevant won cases based on lead's case type"""
        try:
            from ..data.won_cases_db import get_won_cases_by_article
            
            # Try to extract article from case description
            if lead.case_description:
                # Extract article number (e.g., "12.8" from "ч.1 ст.12.8 КоАП РФ")
                import re
                article_match = re.search(r'ст\.\s*(\d+\.?\d*)', lead.case_description)
                if article_match:
                    article = article_match.group(1)
                    won_cases = get_won_cases_by_article(article)
                    return won_cases[:3]  # Return top 3 most relevant
            
            # Fallback: get cases by case type
            case_type_mapping = {
                'DUI': '12.8',
                'SPEEDING': '12.9',
                'LICENSE_SUSPENSION': '12.7',
                'ACCIDENT': '12.27',
            }
            
            if lead.case_type and lead.case_type in case_type_mapping:
                article = case_type_mapping[lead.case_type]
                won_cases = get_won_cases_by_article(article)
                return won_cases[:3]
            
        except Exception as e:
            logger.error(f"Error getting won cases: {e}")
        
        return []
