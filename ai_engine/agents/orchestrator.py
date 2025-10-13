"""
Agent Orchestrator - Lightweight Intent Router
Routes messages to appropriate specialized agents
"""

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Lightweight orchestrator for routing messages to agents
    Uses keyword-based routing first (no API call), AI classification only when needed
    """
    
    # Keyword patterns for intent detection
    INTENT_KEYWORDS = {
        'contract': [
            'договор', 'контракт', 'оформить', 'подписать', 'документ',
            'contract', 'sign'
        ],
        'petition': [
            'ходатайство', 'заявление', 'прошение', 'вернуть права',
            'перенести суд', 'отложить', 'экспертиза'
        ],
        'pricing': [
            'сколько стоит', 'цена', 'тариф', 'стоимость', 'прайс',
            'оплата', 'платить', 'деньги'
        ],
        'verification': [
            r'\b\d{6}\b',  # 6-digit code
            'код', 'подтверждение', 'проверка'
        ],
    }
    
    def __init__(self):
        logger.info("AgentOrchestrator initialized")
    
    def route_message(self, lead, message: str, context: Dict[str, Any]) -> str:
        """
        Route message to appropriate agent
        Returns agent name: 'intake', 'pricing', 'contract', 'petition'
        """
        message_lower = message.lower().strip()
        
        # Priority 1: Verification code (6 digits)
        if self._is_verification_code(message):
            logger.info("Detected verification code - routing to contract agent")
            return 'contract'
        
        # Priority 2: Explicit contract request
        if self._matches_keywords(message_lower, self.INTENT_KEYWORDS['contract']):
            logger.info("Detected contract intent via keywords")
            return 'contract'
        
        # Priority 3: Petition request
        if self._matches_keywords(message_lower, self.INTENT_KEYWORDS['petition']):
            logger.info("Detected petition intent via keywords")
            return 'petition'
        
        # Priority 4: Pricing query
        if self._matches_keywords(message_lower, self.INTENT_KEYWORDS['pricing']):
            logger.info("Detected pricing intent via keywords")
            return 'pricing'
        
        # Priority 5: Check conversation stage
        # Stay in intake for document collection and consultation
        # Only move to pricing when client explicitly asks or after value is shown
        if lead.case_type and not lead.estimated_cost:
            # Check if client is asking about price/cost
            pricing_triggers = ['сколько', 'цена', 'стоимость', 'оплата', 'платить']
            if any(word in message_lower for word in pricing_triggers):
                logger.info("Explicit pricing question - routing to pricing")
                return 'pricing'
            
            # Check if client is ready after receiving value (thanks, what next, etc)
            ready_phrases = ['спасибо за ходатайство', 'что дальше', 'дальше что', 'берем', 'давайте']
            if any(phrase in message_lower for phrase in ready_phrases):
                logger.info("Client ready after value - routing to pricing")
                return 'pricing'
            
            # Otherwise stay in intake for document collection and consultation
            logger.info("Staying in intake for document collection and consultation")
            return 'intake'
        
        # Only route to contract if client EXPLICITLY wants contract
        # Don't route just because lead is HOT - that's too early!
        # Client must first see value (analysis, petition, pricing)
        
        # Default: Intake agent for case analysis
        logger.info("No specific intent detected - routing to intake agent")
        return 'intake'
    
    def _matches_keywords(self, message: str, keywords: list) -> bool:
        """Check if message matches any keyword patterns"""
        for keyword in keywords:
            if keyword.startswith(r'\b'):  # Regex pattern
                if re.search(keyword, message):
                    return True
            else:  # Simple substring match
                if keyword in message:
                    return True
        return False
    
    def _is_verification_code(self, message: str) -> bool:
        """Check if message is a 6-digit verification code"""
        message_clean = message.strip()
        return bool(re.match(r'^\d{6}$', message_clean))
    
    def get_agent_name(self, agent_type: str) -> str:
        """Get full agent class name from type"""
        agent_map = {
            'intake': 'IntakeAgent',
            'pricing': 'PricingAgent',
            'contract': 'ContractAgent',
            'petition': 'PetitionAgent',
        }
        return agent_map.get(agent_type, 'IntakeAgent')
