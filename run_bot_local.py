#!/usr/bin/env python
"""
Local bot runner using simple requests polling
This is for development purposes only
"""
import os
import sys
import django
import logging
import time
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autouristv1.settings')
django.setup()

from django.conf import settings
from ai_engine.services import AIConversationService
from ai_engine.ocr_service import OCRService
from leads.models import Lead

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_file_url(file_id):
    """Get file URL from Telegram"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getFile"
    response = requests.get(url, params={'file_id': file_id})
    
    if response.status_code == 200:
        file_info = response.json()
        if file_info.get('ok'):
            file_path = file_info['result']['file_path']
            return f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"
    return None


def handle_photo_message(message):
    """Handle photo messages with OCR"""
    try:
        # Get the largest photo
        photos = message.get('photo', [])
        if not photos:
            return "Фото не найдено"
        
        # Get the largest photo (last in array)
        largest_photo = photos[-1]
        file_id = largest_photo['file_id']
        
        logger.info(f"Processing photo with file_id: {file_id}")
        
        # Get file URL
        file_url = get_file_url(file_id)
        if not file_url:
            return "Не удалось получить фото"
        
        logger.info(f"Photo URL: {file_url}")
        
        # Process with OCR
        ocr_service = OCRService()
        extracted_text = ocr_service.extract_text_from_image(file_url)
        
        if extracted_text and extracted_text.strip():
            return f"📄 Анализирую документ:\n\n{extracted_text}\n\nРасскажите подробнее о вашей ситуации."
        else:
            return "📷 Фото получено, но текст не распознан. Опишите, пожалуйста, что произошло - какое нарушение, когда, есть ли постановление?"
            
    except Exception as e:
        logger.error(f"Photo processing error: {str(e)}")
        return "📷 Фото получено. Опишите, пожалуйста, вашу ситуацию текстом - какое нарушение, когда произошло, есть ли постановление?"


def handle_document_message(message):
    """Handle document messages"""
    try:
        document = message.get('document')
        if not document:
            return "Документ не найден"
        
        file_name = document.get('file_name', '')
        mime_type = document.get('mime_type', '')
        
        # Check if it's an image document
        if mime_type.startswith('image/'):
            file_id = document['file_id']
            file_url = get_file_url(file_id)
            
            if file_url:
                ocr_service = OCRService()
                extracted_text = ocr_service.extract_text_from_image(file_url)
                
                if extracted_text:
                    return f"📄 Текст из документа {file_name}:\n{extracted_text}"
        
        return f"Получен документ: {file_name}. Для анализа отправьте фото документа или опишите ситуацию текстом."
        
    except Exception as e:
        logger.error(f"Document processing error: {str(e)}")
        return "Ошибка обработки документа. Опишите ситуацию текстом."


def handle_message(message_data):
    """Handle incoming messages"""
    try:
        message = message_data.get('message')
        if not message:
            return
            
        telegram_id = message['from']['id']
        username = message['from'].get('username', '')
        first_name = message['from'].get('first_name', '')
        last_name = message['from'].get('last_name', '')
        message_id = message['message_id']
        
        # Handle different message types
        message_text = ""
        message_type = "text"
        
        if message.get('text'):
            message_text = message.get('text', '')
            message_type = "text"
        elif message.get('photo'):
            message_text = handle_photo_message(message)
            message_type = "photo"
        elif message.get('document'):
            message_text = handle_document_message(message)
            message_type = "document"
        else:
            send_telegram_message(telegram_id, "Пожалуйста, отправьте текстовое сообщение или фото документа.")
            return
        
        logger.info(f"Received message from {telegram_id}: {message_text}")
        
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
        response = ai_service.process_message(lead, message_text, str(message_id))
        
        # Save conversation with message type
        from leads.models import Conversation
        Conversation.objects.create(
            lead=lead,
            message_id=str(message_id),
            user_message=message_text,
            ai_response=response,
            message_type=message_type
        )
        
        # Send response back
        send_telegram_message(telegram_id, response)
        
        logger.info(f"Response sent to {telegram_id}")
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        send_telegram_message(telegram_id, "Извините, произошла техническая ошибка. Попробуйте позже.")


def send_telegram_message(chat_id, text):
    """Send message via Telegram API"""
    # Check if response is a petition document (not just mentions it)
    # Must have: ХОДАТАЙСТВО as title + court address + signature line
    is_petition = (
        'ХОДАТАЙСТВО' in text.upper() and 
        len(text) > 300 and
        ('В ' in text and 'суд' in text.lower()) and  # Court address
        ('Подпись:' in text or 'подпись' in text.lower())  # Signature line
    )
    
    if is_petition:
        # This is a petition document - send as .docx
        send_petition_as_document(chat_id, text)
    else:
        # Regular message
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")


def send_petition_as_document(chat_id, petition_text):
    """Send petition as .docx document"""
    try:
        from ai_engine.services.document_generator import DocumentGenerator
        
        # Generate .docx file
        doc_gen = DocumentGenerator()
        filepath = doc_gen.generate_petition_docx(petition_text)
        
        # Send document via Telegram
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendDocument"
        
        with open(filepath, 'rb') as doc_file:
            files = {'document': doc_file}
            data = {
                'chat_id': chat_id,
                'caption': '📄 Ходатайство готово!\n\n✅ Скачайте документ, распечатайте и подайте в суд.\n\n💡 Также можете отредактировать в Word при необходимости.'
            }
            
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
        
        logger.info(f"Petition document sent to {chat_id}")
        
        # Clean up file after sending
        import os
        os.remove(filepath)
        
    except Exception as e:
        logger.error(f"Failed to send petition as document: {str(e)}")
        # Fallback to text message
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': petition_text,
            'parse_mode': 'HTML'
        }
        requests.post(url, json=payload)


def get_updates(offset=None):
    """Get updates from Telegram"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get updates: {str(e)}")
        return None


def main():
    """Main function to run the bot"""
    logger.info("Starting bot in polling mode...")
    
    offset = None
    
    while True:
        try:
            # Get updates
            updates = get_updates(offset)
            
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    # Process each update
                    handle_message(update)
                    
                    # Update offset
                    offset = update['update_id'] + 1
            
            time.sleep(1)  # Small delay between requests
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Bot error: {str(e)}")
            time.sleep(5)  # Wait before retrying


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
