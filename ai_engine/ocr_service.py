import requests
import logging
from django.conf import settings
from typing import Optional

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR processing using OCR.space API"""
    
    def __init__(self):
        self.api_key = settings.OCR_API_KEY
        self.api_url = "https://api.ocr.space/parse/image"
    
    def extract_text_from_image(self, image_url: str) -> Optional[str]:
        """Extract text from image using OCR.space API"""
        
        try:
            # Download the image first
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            # Prepare the payload
            payload = {
                'apikey': self.api_key,
                'language': 'rus',  # Russian language
                'isOverlayRequired': False,
                'detectOrientation': True,
                'scale': True,
                'OCREngine': 2,  # Engine 2 for better Russian support
                'filetype': 'JPG',  # Explicitly set file type
            }
            
            # Send the file content directly
            files = {'file': ('image.jpg', image_response.content, 'image/jpeg')}
            
            response = requests.post(self.api_url, data=payload, files=files, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('IsErroredOnProcessing'):
                logger.error(f"OCR processing error: {result.get('ErrorMessage')}")
                return None
            
            # Extract text from all parsed results
            extracted_text = ""
            for parsed_result in result.get('ParsedResults', []):
                text = parsed_result.get('ParsedText', '').strip()
                if text:
                    extracted_text += text + "\n"
            
            return extracted_text.strip() if extracted_text else None
            
        except Exception as e:
            logger.error(f"OCR API error: {str(e)}")
            return None
    
    def extract_text_from_file(self, file_path: str) -> Optional[str]:
        """Extract text from local file using OCR.space API"""
        
        payload = {
            'apikey': self.api_key,
            'language': 'rus',
            'isOverlayRequired': False,
            'detectOrientation': True,
            'scale': True,
            'OCREngine': 2,
        }
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(self.api_url, data=payload, files=files, timeout=30)
                response.raise_for_status()
            
            result = response.json()
            
            if result.get('IsErroredOnProcessing'):
                logger.error(f"OCR processing error: {result.get('ErrorMessage')}")
                return None
            
            # Extract text from all parsed results
            extracted_text = ""
            for parsed_result in result.get('ParsedResults', []):
                text = parsed_result.get('ParsedText', '').strip()
                if text:
                    extracted_text += text + "\n"
            
            return extracted_text.strip() if extracted_text else None
            
        except Exception as e:
            logger.error(f"OCR file processing error: {str(e)}")
            return None
