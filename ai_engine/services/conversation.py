import logging
import os
from decimal import Decimal
from typing import Dict, List

from django.conf import settings

from leads.models import Lead, Conversation

from .deepseek import DeepSeekAPIService
from ai_engine.services.memory import ConversationMemoryService
from ai_engine.services.contracts_flow import ContractFlow

# Multi-agent imports
from ..agents.orchestrator import AgentOrchestrator
from ..agents import AGENT_REGISTRY
logger = logging.getLogger(__name__)


class AIConversationService:
    """Main service for handling AI conversations"""

    def __init__(self):
        self.deepseek = DeepSeekAPIService()
        self.memory = ConversationMemoryService()
        self.contract_flow = ContractFlow()
        self.pricing_data = analytics.load_pricing_data()
        
        # Multi-agent system (feature flag)
        self.use_multi_agent = os.getenv('USE_MULTI_AGENT', 'True') == 'True'
        if self.use_multi_agent:
            self.orchestrator = AgentOrchestrator()
            logger.info("Multi-agent system enabled")
        else:
            logger.info("Using legacy single-agent system")

    def process_message(self, lead: Lead, message: str, message_id: str) -> str:
        try:
            logger.info(f"Processing message from lead {lead.telegram_id}: {message[:100]}...")
            
            # Handle /start command - clear conversation and greet
            if message.strip().lower() in ['/start', 'start', 'начать']:
                logger.info(f"Start command received from {lead.telegram_id}")
                self.memory.clear_conversation(lead.telegram_id)
                return self._get_greeting_message(lead)
            
            # Route to appropriate processing method
            if self.use_multi_agent:
                ai_response = self._process_with_agents(lead, message)
            else:
                ai_response = self._process_legacy(lead, message)
            
            processed_response = self._process_response_commands(lead, ai_response, message)
            logger.debug(f"Processed response: {processed_response[:200]}...")

            Conversation.objects.create(
                lead=lead,
                message_id=message_id,
                user_message=message,
                ai_response=processed_response,
            )

            self.memory.add_message(lead.telegram_id, message, processed_response)
            lead.last_interaction = timezone.now()
            lead.save()
            
            # Schedule follow-up message after 1 hour if lead doesn't respond
            try:
                from contract_manager.tasks import send_follow_up_message_task
                # Schedule task to run in 1 hour (3600 seconds)
                send_follow_up_message_task.apply_async(
                    args=[lead.telegram_id, lead.id],
                    countdown=3600  # 1 hour
                )
                logger.info(f"Scheduled follow-up for lead {lead.id} in 1 hour")
            except Exception as e:
                logger.warning(f"Could not schedule follow-up task: {e}")

            return processed_response
        except Exception as e:
            logger.error(f"AI conversation error: {str(e)}")
            return (
                "Извините, произошла техническая ошибка. Наш менеджер скоро с вами свяжется."
            )

    def _process_response_commands(self, lead: Lead, response: str, user_message: str) -> str:
        import re

        commands = re.findall(r"\[([A-Z_]+):?([^\]]*)\]", response)
        logger.info(f"Found {len(commands)} commands in response: {[cmd[0] for cmd in commands]}")
        
        # Process commands that need immediate return (document generation, etc.)
        for command, params in commands:
            try:
                logger.debug(f"Processing command: {command} with params: {params[:100] if params else 'None'}...")
                
                # Commands that generate and send documents - return immediately
                if command == "GENERATE_CONTRACT":
                    logger.info(f"Generating contract for lead {lead.telegram_id} with params: {params}")
                    return self.contract_flow.handle_contract_generation(lead, params)
                elif command == "GENERATE_PETITION":
                    logger.info(f"Generating petition for lead {lead.telegram_id} with params: {params}")
                    # Import document generator
                    from ai_engine.services.document_generator import DocumentGenerator
                    doc_gen = DocumentGenerator()
                    # Generate petition and send it
                    return doc_gen.generate_and_send_petition(lead, params)
                elif command == "SEND_SMS_CODE":
                    return self.contract_flow.handle_sms_code(lead)
                elif command == "VERIFY_SMS":
                    return self.contract_flow.handle_sms_verification(lead, params)
                    
            except Exception as e:
                logger.error(f"Command processing error: {str(e)}")
                logger.exception("Command error traceback:")
                # Return error message if document generation fails
                return f"❌ Произошла ошибка: {str(e)}\n\nПопробуйте еще раз или обратитесь к менеджеру."
        
        # Process state-update commands (don't return, just update lead)
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
                elif command == "TRANSFER_TO_LAWYER":
                    lead.status = "FOLLOW_UP"
                    lead.save()
            except Exception as e:
                logger.error(f"State update command error: {str(e)}")

        # Clean response by removing command tags
        clean_response = re.sub(r"\[[A-Z_]+:?[^\]]*\]", "", response).strip()
        return clean_response
    
    def _process_with_agents(self, lead: Lead, message: str) -> str:
        """Process message using multi-agent system"""
        logger.info("Using multi-agent system")
        
        # Build context
        context = {
            'conversation_history': self.memory.get_conversation_history(lead.telegram_id),
            'pricing_data': self.pricing_data,
        }
        
        # Route to appropriate agent
        agent_type = self.orchestrator.route_message(lead, message, context)
        logger.info(f"Routed to agent: {agent_type}")
        
        # Get agent class and instantiate
        agent_class = AGENT_REGISTRY.get(agent_type)
        if not agent_class:
            logger.error(f"Agent not found: {agent_type}")
            return "Извините, произошла ошибка маршрутизации."
        
        agent = agent_class(self.deepseek, self.memory)
        
        # Process message with agent
        response = agent.process(lead, message, context)
        logger.info(f"Agent {agent_type} response: {response[:200]}...")
        
        return response
    
    def _process_legacy(self, lead: Lead, message: str) -> str:
        """Process message using legacy single-agent system"""
        logger.info("Using legacy system")
        
        conversation_history = self.memory.get_conversation_history(lead.telegram_id)
        logger.debug(f"Conversation history length: {len(conversation_history)}")

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

        logger.debug(f"Sending {len(messages)} messages to DeepSeek API")
        ai_response = self.deepseek.chat_completion(messages)
        logger.info(f"AI response received: {ai_response[:200]}...")
        
        return ai_response
    
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
