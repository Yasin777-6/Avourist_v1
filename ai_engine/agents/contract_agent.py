"""
Contract Agent - Contract Generation & Signing
Collects client data and generates contracts
"""

import logging
from typing import Dict, Any
from .base import BaseAgent
from ..prompts.contract_prompt import CONTRACT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ContractAgent(BaseAgent):
    """
    Specialized agent for contract generation and signing workflow
    Handles data collection, contract generation, and verification
    """
    
    def process(self, lead, message: str, context: Dict[str, Any]) -> str:
        """Process message for contract workflow"""
        logger.info(f"ContractAgent processing message for lead {lead.telegram_id}")
        
        # Check if message is a verification code (6 digits)
        if self._is_verification_code(message):
            logger.info("Message appears to be verification code")
            # Let the response include [VERIFY_SMS:code] command
        
        # Build messages for AI
        messages = self.build_messages(lead, message, context)
        
        # Call AI
        response = self.call_ai(messages, temperature=0.4)
        
        logger.info(f"ContractAgent response generated for lead {lead.telegram_id}")
        return response
    
    def get_system_prompt(self, lead, context: Dict[str, Any]) -> str:
        """Get contract-specific system prompt"""
        return CONTRACT_SYSTEM_PROMPT(lead, context)
    
    def _is_verification_code(self, message: str) -> bool:
        """Check if message is a 6-digit verification code"""
        import re
        return bool(re.match(r'^\d{6}$', message.strip()))
