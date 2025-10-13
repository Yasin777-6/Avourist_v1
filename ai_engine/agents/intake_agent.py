"""
Intake Agent - Article Identification & Case Analysis
Identifies КоАП РФ article from user description
"""

import logging
from typing import Dict, Any
from .base import BaseAgent
from ..prompts.intake_prompt import INTAKE_SYSTEM_PROMPT
from ..data.knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)


class IntakeAgent(BaseAgent):
    """
    Specialized agent for case intake and article identification
    Determines КоАП РФ article and provides initial case analysis
    Uses knowledge base for accurate article matching
    """
    
    def __init__(self, deepseek_service, memory_service=None):
        super().__init__(deepseek_service, memory_service)
        self.kb = get_knowledge_base()
    
    def process(self, lead, message: str, context: Dict[str, Any]) -> str:
        """Process message for case intake and article identification"""
        logger.info(f"IntakeAgent processing message for lead {lead.telegram_id}")
        
        # Try to find article from knowledge base
        article_match = self.kb.find_article_by_keywords(message)
        if article_match:
            logger.info(f"Knowledge base matched: {article_match['article']}")
            context['suggested_article'] = article_match
        
        # Build messages for AI
        messages = self.build_messages(lead, message, context)
        
        # Call AI with lower temperature for more precise article identification
        response = self.call_ai(messages, temperature=0.5)
        
        logger.info(f"IntakeAgent response generated for lead {lead.telegram_id}")
        return response
    
    def get_system_prompt(self, lead, context: Dict[str, Any]) -> str:
        """Get intake-specific system prompt with knowledge base context"""
        prompt = INTAKE_SYSTEM_PROMPT(lead, context)
        
        # Add suggested article if found
        if context.get('suggested_article'):
            article = context['suggested_article']
            prompt += f"\n\n<b>Подсказка из базы знаний:</b>\n"
            prompt += f"Похоже на {article['article']} - {article['title']}\n"
            prompt += f"Наказание: {article['punishment'].get('fine', '')} + {article['punishment'].get('license_suspension', '')}\n"
        
        return prompt
