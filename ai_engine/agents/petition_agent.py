"""
Petition Agent - Legal Petition Generation
Generates ходатайства (petitions) for court
"""

import logging
from typing import Dict, Any
from .base import BaseAgent
from ..prompts.petition_prompt import PETITION_SYSTEM_PROMPT
from ..data.knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)


class PetitionAgent(BaseAgent):
    """
    Specialized agent for generating legal petitions (ходатайства)
    Creates court documents based on client needs
    Uses knowledge base templates for accurate legal formatting
    """
    
    PETITION_TYPES = {
        'возврат прав': 'return_license',
        'перенос суд': 'postpone_hearing',
        'отложить': 'postpone_case',
        'экспертиза': 'request_expertise',
        'свидетел': 'call_witnesses',
        'ознакомлен': 'review_materials',
        'ознакомление': 'review_materials_detailed',
        'привлечен': 'attract_representative',
        'представител': 'attract_representative',
        'получени': 'obtain_court_acts',
        'судебн акт': 'obtain_court_acts',
    }
    
    def __init__(self, deepseek_service, memory_service=None):
        super().__init__(deepseek_service, memory_service)
        self.kb = get_knowledge_base()
    
    def process(self, lead, message: str, context: Dict[str, Any]) -> str:
        """Process message for petition generation"""
        logger.info(f"PetitionAgent processing message for lead {lead.telegram_id}")
        
        # Detect petition type
        petition_type = self._detect_petition_type(message)
        if petition_type:
            logger.info(f"Detected petition type: {petition_type}")
            context['petition_type'] = petition_type
            
            # Get template from knowledge base
            template = self.kb.get_petition_template(petition_type)
            if template:
                logger.info(f"Found template: {template['title']}")
                context['petition_template'] = template
        
        # Build messages for AI
        messages = self.build_messages(lead, message, context)
        
        # Call AI with higher temperature for creative legal writing
        response = self.call_ai(messages, temperature=0.7)
        
        logger.info(f"PetitionAgent response generated for lead {lead.telegram_id}")
        return response
    
    def get_system_prompt(self, lead, context: Dict[str, Any]) -> str:
        """Get petition-specific system prompt with template context"""
        prompt = PETITION_SYSTEM_PROMPT(lead, context)
        
        # Add template if found
        if context.get('petition_template'):
            template = context['petition_template']
            prompt += f"\n\n<b>Шаблон из базы знаний:</b>\n"
            prompt += f"Тип: {template['title']}\n"
            prompt += f"Обязательные поля: {', '.join(template['required_fields'])}\n\n"
            prompt += f"<b>Шаблон:</b>\n{template['template'][:500]}...\n"
        
        return prompt
    
    def _detect_petition_type(self, message: str) -> str:
        """Detect petition type from message keywords"""
        message_lower = message.lower()
        for keyword, petition_type in self.PETITION_TYPES.items():
            if keyword in message_lower:
                return petition_type
        return None
