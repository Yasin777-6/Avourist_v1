import logging
from typing import Dict, List

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class DeepSeekAPIService:
    """Service for interacting with DeepSeek API"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat_completion(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """Send chat completion request to DeepSeek API"""
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1200,  # Increased for detailed problem analysis and solutions
            "stream": False,
        }
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            return "Извините, произошла техническая ошибка. Попробуйте позже."
