"""
Base Agent Class
All specialized agents inherit from this
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, deepseek_service, memory_service=None):
        self.deepseek = deepseek_service
        self.memory = memory_service
        self.agent_name = self.__class__.__name__
        logger.info(f"Initialized {self.agent_name}")
    
    @abstractmethod
    def process(self, lead, message: str, context: Dict[str, Any]) -> str:
        """
        Process user message and return response
        Must be implemented by subclasses
        """
        raise NotImplementedError(f"{self.agent_name} must implement process()")
    
    @abstractmethod
    def get_system_prompt(self, lead, context: Dict[str, Any]) -> str:
        """
        Get agent-specific system prompt
        Must be implemented by subclasses
        """
        raise NotImplementedError(f"{self.agent_name} must implement get_system_prompt()")
    
    def build_messages(self, lead, message: str, context: Dict[str, Any]) -> list:
        """Build message list for DeepSeek API"""
        system_prompt = self.get_system_prompt(lead, context)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if self.memory:
            history = self.memory.get_conversation_history(lead.telegram_id)
            for msg in history[-5:]:  # Last 5 messages for context
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def call_ai(self, messages: list, temperature: float = 0.7) -> str:
        """Call DeepSeek API with messages"""
        try:
            response = self.deepseek.chat_completion(messages, temperature)
            logger.debug(f"{self.agent_name} AI response: {response[:200]}...")
            return response
        except Exception as e:
            logger.error(f"{self.agent_name} AI call failed: {e}")
            return "Извините, произошла техническая ошибка. Попробуйте позже."
    
    def extract_context_data(self, lead) -> Dict[str, Any]:
        """Extract relevant data from lead for context"""
        return {
            'case_type': lead.case_type,
            'case_description': lead.case_description,
            'status': lead.status,
            'region': lead.region,
            'estimated_cost': str(lead.estimated_cost) if lead.estimated_cost else None,
            'win_probability': lead.win_probability,
        }
