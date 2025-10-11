"""
Celery tasks for contract_manager app
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

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
