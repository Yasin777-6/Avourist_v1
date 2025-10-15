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
    
    def set_last_interaction(self, telegram_id: int):
        """Set last interaction timestamp for follow-up tracking"""
        key = f"last_interaction:{telegram_id}"
        try:
            self.redis_client.setex(key, 3600 * 2, datetime.now().isoformat())  # 2 hours TTL
        except Exception as e:
            logger.error(f"Redis set last_interaction error: {str(e)}")
    
    def get_last_interaction(self, telegram_id: int) -> datetime:
        """Get last interaction timestamp"""
        key = f"last_interaction:{telegram_id}"
        try:
            timestamp_str = self.redis_client.get(key)
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str.decode('utf-8'))
        except Exception as e:
            logger.error(f"Redis get last_interaction error: {str(e)}")
        return None
    
    def should_send_follow_up(self, telegram_id: int) -> bool:
        """Check if follow-up message should be sent (1 hour of inactivity)"""
        last_interaction = self.get_last_interaction(telegram_id)
        if not last_interaction:
            return False
        
        from datetime import timedelta
        one_hour_ago = datetime.now() - timedelta(hours=1)
        return last_interaction < one_hour_ago
