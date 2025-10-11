import logging
from decimal import Decimal
from typing import Dict, List

from django.utils import timezone

from leads.models import Lead, Conversation

from .deepseek import DeepSeekAPIService
from .memory import ConversationMemoryService
from .contracts_flow import ContractFlow
from . import analytics
from . import prompts

logger = logging.getLogger(__name__)


class AIConversationService:
    """Main service for handling AI conversations"""

    def __init__(self):
        self.deepseek = DeepSeekAPIService()
        self.memory = ConversationMemoryService()
        self.contract_flow = ContractFlow()
        self.pricing_data = analytics.load_pricing_data()

    def process_message(self, lead: Lead, message: str, message_id: str) -> str:
        try:
            # Handle /start command - clear conversation and greet
            if message.strip().lower() in ['/start', 'start', 'начать']:
                self.memory.clear_conversation(lead.telegram_id)
                return self._get_greeting_message(lead)
            
            conversation_history = self.memory.get_conversation_history(lead.telegram_id)

            current_stage = prompts.get_current_stage(lead)
            region_pricing = self.pricing_data.get(lead.region, self.pricing_data["REGIONS"])
            formatted_pricing = analytics.format_pricing_for_prompt(region_pricing)

            system_prompt = prompts.build_system_prompt(
                lead=lead,
                current_stage=current_stage,
                formatted_pricing=formatted_pricing,
            )

            messages: List[Dict] = [{"role": "system", "content": system_prompt}]
            for msg in conversation_history[-10:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
            messages.append({"role": "user", "content": message})

            ai_response = self.deepseek.chat_completion(messages)
            processed_response = self._process_response_commands(lead, ai_response, message)

            Conversation.objects.create(
                lead=lead,
                message_id=message_id,
                user_message=message,
                ai_response=processed_response,
            )

            self.memory.add_message(lead.telegram_id, message, processed_response)
            lead.last_interaction = timezone.now()
            lead.save()

            return processed_response
        except Exception as e:
            logger.error(f"AI conversation error: {str(e)}")
            return (
                "Извините, произошла техническая ошибка. Наш менеджер скоро с вами свяжется."
            )

    def _process_response_commands(self, lead: Lead, response: str, user_message: str) -> str:
        import re

        commands = re.findall(r"\[([A-Z_]+):?([^\]]*)\]", response)
        for command, params in commands:
            try:
                if command == "UPDATE_LEAD_STATUS":
                    if params in ["HOT", "WARM", "COLD", "CONSULTATION"]:
                        lead.status = params
                        lead.save()
                elif command == "UPDATE_CASE_TYPE":
                    case_mapping = {
                        "пьяное вождение": "DUI",
                        "превышение скорости": "SPEEDING",
                        "лишение прав": "LICENSE_SUSPENSION",
                        "дтп": "ACCIDENT",
                        "парковка": "PARKING",
                    }
                    case_type = case_mapping.get(params.lower(), "OTHER")
                    lead.case_type = case_type
                    lead.save()
                elif command == "UPDATE_CASE_DESCRIPTION":
                    lead.case_description = params
                    lead.save()
                elif command == "SET_ANALYSIS":
                    try:
                        parts = params.split(",")
                        if len(parts) >= 2:
                            lead.estimated_cost = Decimal(parts[0].strip())
                            lead.win_probability = int(parts[1].strip())
                            lead.save()
                    except (ValueError, IndexError):
                        pass
                elif command == "GENERATE_CONTRACT":
                    return self.contract_flow.handle_contract_generation(lead, params)
                elif command == "SEND_SMS_CODE":
                    return self.contract_flow.handle_sms_code(lead)
                elif command == "VERIFY_SMS":
                    return self.contract_flow.handle_sms_verification(lead, params)
                elif command == "TRANSFER_TO_LAWYER":
                    lead.status = "FOLLOW_UP"
                    lead.save()
            except Exception as e:
                logger.error(f"Command processing error: {str(e)}")

        clean_response = re.sub(r"\[[A-Z_]+:?[^\]]*\]", "", response).strip()
        return clean_response
    
    def _get_greeting_message(self, lead: Lead) -> str:
        """Get greeting message for new conversation"""
        name = lead.first_name or "Клиент"
        return f"""Здравствуйте, {name}! Я Алексей, юрист АвтоЮрист.

Помогу с:
• Лишением прав
• Оспариванием штрафов
• ДТП и авариями
• Другими нарушениями

Расскажите вашу ситуацию — дам оценку шансов и помогу защитить ваши права."""
