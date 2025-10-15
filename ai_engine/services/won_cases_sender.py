"""
Won Cases Sender - Sends court document images to clients
"""

import logging
import requests
from django.conf import settings
from ai_engine.data.won_cases_db import get_won_cases_by_article

logger = logging.getLogger(__name__)


def send_won_case_images(telegram_id: int, article: str):
    """
    Send court document images for won cases to client
    
    Args:
        telegram_id: Telegram user ID
        article: Article number (e.g., "12.8" for DUI or "Статья: 12.8 КоАП")
    """
    try:
        # Extract just the article number (e.g., "12.8" from "Статья: 12.8 КоАП")
        import re
        article_match = re.search(r'(\d+\.\d+)', article)
        if article_match:
            article = article_match.group(1)
        
        logger.info(f"Looking for won cases with article: {article}")
        
        # Get won cases for this article
        won_cases = get_won_cases_by_article(article)
        
        if not won_cases:
            logger.warning(f"No won cases found for article {article}")
            return
        
        # Get bot token
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        # Send images from first case with images
        images_sent = 0
        for case in won_cases:
            if case.get('images') and len(case['images']) > 0:
                # Send up to 3 images
                for img_data in case['images'][:3]:
                    img_url = img_data.get('url')
                    if img_url:
                        try:
                            # URL-encode the image URL (handle Cyrillic characters)
                            from urllib.parse import quote
                            # Split URL into base and filename
                            parts = img_url.rsplit('/', 1)
                            if len(parts) == 2:
                                base_url, filename = parts
                                # Encode only the filename part
                                encoded_filename = quote(filename)
                                img_url = f"{base_url}/{encoded_filename}"
                            
                            # Download image first
                            logger.info(f"Downloading image from {img_url}")
                            img_response = requests.get(img_url, timeout=30)
                            
                            if img_response.status_code != 200:
                                logger.error(f"Failed to download image: {img_response.status_code}")
                                continue
                            
                            # Send as document (not photo) for better quality/zoom
                            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
                            caption = f"📄 {case.get('title', 'Выигранное дело')}\n\n💡 Откройте файл для увеличения и чтения"
                            
                            files = {
                                'document': (img_data.get('filename', 'document.jpg'), img_response.content, 'image/jpeg')
                            }
                            data = {
                                'chat_id': telegram_id,
                                'caption': caption,
                                'parse_mode': 'HTML'
                            }
                            
                            response = requests.post(url, files=files, data=data, timeout=30)
                            
                            if response.status_code == 200:
                                images_sent += 1
                                logger.info(f"Sent won case image to {telegram_id}: {img_url}")
                            else:
                                logger.error(f"Failed to send image: {response.text}")
                        
                        except Exception as e:
                            logger.error(f"Error sending image {img_url}: {e}")
                
                # Stop after sending images from first case
                if images_sent > 0:
                    break
        
        if images_sent > 0:
            logger.info(f"Successfully sent {images_sent} won case images to {telegram_id}")
        else:
            logger.warning(f"No images found for article {article}")
    
    except Exception as e:
        logger.error(f"Error in send_won_case_images: {e}")
        logger.exception("Full traceback:")
