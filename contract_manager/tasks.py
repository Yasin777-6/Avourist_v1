"""
Celery tasks for contract_manager app and lead follow-up
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, email: str, code: str, contract_number: str):
    """
    Async task to send verification code via email
    
    Args:
        email: Recipient email address
        code: Verification code
        contract_number: Contract number for reference
    """
    logger.info(f"=== EMAIL TASK STARTED ===")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Recipient: {email}")
    logger.info(f"Contract: {contract_number}")
    logger.info(f"Code: {code}")
    
    if not email:
        logger.warning(f"No email address for contract {contract_number}")
        return
    
    subject = f"Код подтверждения договора {contract_number}"
    message = f"""
Здравствуйте!

Ваш код подтверждения договора: {code}

Код действителен 10 минут.

Введите этот код в Telegram-боте для подписания договора.

---
С уважением,
Команда АвтоЮрист
    """.strip()
    
    try:
        logger.info(f"Sending email from {settings.DEFAULT_FROM_EMAIL} to {email}")
        logger.info(f"Email backend: {settings.EMAIL_BACKEND}")
        logger.info(f"Email host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"✅ Verification code sent successfully to {email}")
        return f"Email sent successfully to {email}"
    except Exception as e:
        logger.error(f"❌ Failed to send email to {email}: {e}")
        logger.exception("Full traceback:")
        # Retry the task
        raise self.retry(exc=e)


@shared_task
def send_follow_up_message_task(telegram_id: int, lead_id: int):
    """
    Send follow-up message to inactive leads after 1 hour
    
    Args:
        telegram_id: Telegram user ID
        lead_id: Lead ID
    """
    from leads.models import Lead
    from ai_engine.services.conversation import ConversationService
    import requests
    
    logger.info(f"=== FOLLOW-UP TASK STARTED ===")
    logger.info(f"Telegram ID: {telegram_id}, Lead ID: {lead_id}")
    
    try:
        lead = Lead.objects.get(id=lead_id, telegram_id=telegram_id)
        
        # Check if lead has responded in the last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        # Get conversation history
        conversation_service = ConversationService()
        history = conversation_service._get_conversation_history(lead)
        
        if not history:
            logger.info(f"No conversation history for lead {lead_id}")
            return
        
        # Check last message timestamp
        last_message = history[-1]
        if 'timestamp' in last_message:
            # If client responded recently, don't send follow-up
            return
        
        # Determine follow-up message based on lead status
        follow_up_messages = {
            'NEW': """Понимаю 😊 Просто напомню — могу бесплатно помочь:

<b>Что я могу сделать прямо сейчас:</b>
• Найти ваше дело в базе суда
• Подготовить заявление на ознакомление с материалами
• Оценить шансы по базе выигранных дел

<b>Хотите бесплатную консультацию?</b> Оставьте телефон, юрист свяжется в течение часа.""",
            
            'WARM': """Напоминаю — у вас всего 10 дней на обжалование с момента получения постановления ⏰

<b>Могу бесплатно подготовить:</b>
• Ходатайство на ознакомление с делом
• Заявление о переносе суда
• Анализ шансов по вашей статье

<b>Не теряйте время!</b> Оставьте телефон, и юрист свяжется сегодня.""",
            
            'HOT': """Вижу, вы заинтересованы в защите своих прав 👍

<b>Готов помочь прямо сейчас:</b>
• Покажу примеры выигранных дел
• Подготовлю бесплатное ходатайство
• Дам консультацию по вашей ситуации

<b>Оставьте телефон</b> — юрист свяжется и расскажет, как сохранить права."""
        }
        
        message = follow_up_messages.get(lead.status, follow_up_messages['NEW'])
        
        # Send message via Telegram
        bot_token = settings.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        response = requests.post(url, json={
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'HTML'
        })
        
        if response.status_code == 200:
            logger.info(f"✅ Follow-up message sent to {telegram_id}")
            
            # Update lead's last_contact
            lead.last_contact = timezone.now()
            lead.save()
        else:
            logger.error(f"❌ Failed to send follow-up: {response.text}")
            
    except Lead.DoesNotExist:
        logger.error(f"Lead {lead_id} not found")
    except Exception as e:
        logger.error(f"Error in follow-up task: {e}")
        logger.exception("Full traceback:")
