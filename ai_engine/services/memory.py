import json
import logging
from datetime import datetime
from typing import Dict, List

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


class ConversationMemoryService:
    """Service for managing conversation memory using Redis"""

    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.memory_ttl = 3600 * 24  # 24 hours

    def get_conversation_history(self, telegram_id: int) -> List[Dict]:
        """Get conversation history from Redis"""
        key = f"conversation:{telegram_id}"
        try:
            history_json = self.redis_client.get(key)
            if history_json:
                return json.loads(history_json)
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
        return []

    def add_message(self, telegram_id: int, user_message: str, ai_response: str):
        """Add message to conversation history"""
        key = f"conversation:{telegram_id}"
        try:
            history = self.get_conversation_history(telegram_id)
            history.append(
                {
                    "user": user_message,
                    "assistant": ai_response,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            if len(history) > 20:
                history = history[-20:]
            self.redis_client.setex(key, self.memory_ttl, json.dumps(history, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")

    def clear_conversation(self, telegram_id: int):
        """Clear conversation history"""
        key = f"conversation:{telegram_id}"
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
