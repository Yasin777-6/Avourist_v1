"""
Pricing Agent - ROI Calculation & Cost Analysis
Calculates costs and shows client savings
"""

import logging
from typing import Dict, Any
from .base import BaseAgent
from ..prompts.pricing_prompt import PRICING_SYSTEM_PROMPT
from ..services import analytics

logger = logging.getLogger(__name__)


class PricingAgent(BaseAgent):
    """
    Specialized agent for pricing calculations and ROI analysis
    Shows client the financial benefit of legal representation
    """
    
    def __init__(self, deepseek_service, memory_service=None):
        super().__init__(deepseek_service, memory_service)
        self.pricing_data = analytics.load_pricing_data()
    
    def process(self, lead, message: str, context: Dict[str, Any]) -> str:
        """Process message for pricing and ROI calculation"""
        logger.info(f"PricingAgent processing message for lead {lead.telegram_id}")
        
        # Build messages for AI
        messages = self.build_messages(lead, message, context)
        
        # Call AI
        response = self.call_ai(messages, temperature=0.6)
        
        logger.info(f"PricingAgent response generated for lead {lead.telegram_id}")
        return response
    
    def get_system_prompt(self, lead, context: Dict[str, Any]) -> str:
        """Get pricing-specific system prompt with pricing data"""
        region_pricing = self.pricing_data.get(lead.region, self.pricing_data["REGIONS"])
        formatted_pricing = analytics.format_pricing_for_prompt(region_pricing)
        
        return PRICING_SYSTEM_PROMPT(lead, context, formatted_pricing)
