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
        
        # Check if lead has responded in the last hour using Redis
        from ai_engine.services.memory import ConversationMemoryService
        memory_service = ConversationMemoryService()
        
        # Check last interaction timestamp from Redis
        last_interaction = memory_service.get_last_interaction(telegram_id)
        
        if last_interaction:
            # If client interacted in the last hour, don't send follow-up
            one_hour_ago = timezone.now() - timedelta(hours=1)
            if last_interaction.replace(tzinfo=None) > one_hour_ago.replace(tzinfo=None):
                logger.info(f"Lead {lead_id} interacted recently, skipping follow-up")
                return
        
        # Check if we already sent a follow-up
        follow_up_key = f"follow_up_sent:{telegram_id}"
        if memory_service.redis_client.get(follow_up_key):
            logger.info(f"Follow-up already sent to {telegram_id}, skipping")
            return
        
        # Mark that we're sending a follow-up (prevent duplicates)
        memory_service.redis_client.setex(follow_up_key, 3600 * 24, "1")  # 24 hours
        
        # Determine follow-up message based on lead status
        follow_up_messages = {
            'NEW': """Привет! 👋 Я все еще здесь и готов помочь.

<b>Могу прямо сейчас бесплатно:</b>
• 📊 Оценить ваши шансы на успех (в процентах)
• 📄 Подготовить ходатайство об ознакомлении с делом (файл .docx)
• 🎯 Найти процессуальные нарушения в вашем деле
• ⚖️ Показать примеры выигранных дел по вашей статье

<b>Просто опишите вашу ситуацию</b> — я дам конкретный анализ и подготовлю документы.""",
            
            'WARM': """⏰ <b>Напоминаю:</b> у вас всего 10 дней на обжалование!

<b>Давайте я помогу прямо сейчас (бесплатно):</b>
• 📊 Оценю ваши шансы на успех (в процентах)
• 📄 Подготовлю ходатайство об ознакомлении с материалами дела (файл .docx)
• 📄 Подготовлю ходатайство о привлечении защитника (файл .docx)
• 🎯 Найду нарушения ГИБДД в протоколе

<b>Для ходатайства нужно всего 3 вещи:</b>
• Ваше ФИО полностью
• Адрес регистрации
• Город (где было нарушение)

Напишите эти данные, и я сразу подготовлю ходатайство в формате .docx.""",
            
            'HOT': """🎯 <b>Готов помочь прямо сейчас!</b>

<b>Что я могу сделать бесплатно:</b>
• 📊 Оценить шансы на успех (в процентах) — покажу реальную статистику
• 📄 Подготовить ходатайство для суда (файл .docx) — готово за 1 минуту
• 🎯 Найти процессуальные нарушения — покажу все зацепки для защиты
• ⚖️ Показать примеры выигранных дел — увидите реальные кейсы

<b>Для ходатайства нужно всего 3 вещи:</b>
• Ваше ФИО полностью
• Адрес регистрации
• Город (где было нарушение)

Напишите одной строкой, например: Иванов Иван Иванович, г. Москва ул. Ленина 10, Москва"""
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
