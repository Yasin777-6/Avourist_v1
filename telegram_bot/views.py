import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from ai_engine.services import AIConversationService
from leads.models import Lead, Conversation
from contract_manager.models import Contract, SMSVerification

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """Handle incoming Telegram webhook messages"""
    
    def post(self, request):
        try:
            # Parse incoming webhook data
            data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Received webhook: {data}")
            
            # Extract message info
            message = data.get('message')
            if not message:
                return JsonResponse({'status': 'ok'})
            
            telegram_id = message['from']['id']
            username = message['from'].get('username', '')
            first_name = message['from'].get('first_name', '')
            last_name = message['from'].get('last_name', '')
            message_text = message.get('text', '')
            message_id = message['message_id']
            
            # Get or create lead
            lead, created = Lead.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            
            # Update lead info if not created
            if not created:
                lead.username = username
                lead.first_name = first_name  
                lead.last_name = last_name
                lead.save()
            
            # Process message through AI
            ai_service = AIConversationService()
            response = ai_service.process_message(lead, message_text, message_id)
            
            # Send response back to Telegram
            self._send_telegram_message(telegram_id, response)
            
            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    def _send_telegram_message(self, telegram_id, message):
        """Send message back to Telegram user"""
        import requests
        from django.conf import settings
        
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': telegram_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Message sent to {telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")


@csrf_exempt
@require_POST
def set_webhook(request):
    """Set up Telegram webhook"""
    import requests
    from django.conf import settings
    
    webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/telegram/webhook/"
    telegram_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
    
    payload = {'url': webhook_url}
    response = requests.post(telegram_url, json=payload)
    
    if response.status_code == 200:
        return JsonResponse({'status': 'success', 'webhook_set': webhook_url})
    else:
        return JsonResponse({'status': 'error', 'response': response.text})


def webhook_info(request):
    """Get webhook info"""
    import requests
    from django.conf import settings
    
    telegram_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    response = requests.get(telegram_url)
    
    return JsonResponse(response.json())
