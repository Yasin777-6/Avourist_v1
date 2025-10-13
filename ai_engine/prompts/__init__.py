"""
Agent-specific prompts
Split from monolithic prompts.py for better maintainability
"""

from .intake_prompt import INTAKE_SYSTEM_PROMPT
from .pricing_prompt import PRICING_SYSTEM_PROMPT
from .contract_prompt import CONTRACT_SYSTEM_PROMPT
from .petition_prompt import PETITION_SYSTEM_PROMPT

__all__ = [
    'INTAKE_SYSTEM_PROMPT',
    'PRICING_SYSTEM_PROMPT',
    'CONTRACT_SYSTEM_PROMPT',
    'PETITION_SYSTEM_PROMPT',
]
