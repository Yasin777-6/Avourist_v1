"""
Multi-Agent System for AvtoUrist AI Bot
Specialized agents for different conversation tasks
"""

from .base import BaseAgent
from .orchestrator import AgentOrchestrator
from .intake_agent import IntakeAgent
from .pricing_agent import PricingAgent
from .contract_agent import ContractAgent
from .petition_agent import PetitionAgent

__all__ = [
    'BaseAgent',
    'AgentOrchestrator',
    'IntakeAgent',
    'PricingAgent',
    'ContractAgent',
    'PetitionAgent',
]

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    'intake': IntakeAgent,
    'pricing': PricingAgent,
    'contract': ContractAgent,
    'petition': PetitionAgent,
}
