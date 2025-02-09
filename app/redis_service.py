import redis
from redis.exceptions import ConnectionError
from .config import settings
from .chat import ChatSession
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db
        )
        logger.info("Redis Service initialized")

    async def save_chat_session(self, chat_session: ChatSession):
        try:
            self.redis_client.set(
                f"chat:{chat_session.session_id}",
                chat_session.model_dump_json()
            )
            logger.info(f"Chat session saved successfully: {chat_session.session_id}")

        except ConnectionError as e:
            logger.error(f"Redis connection error during save: {e}")

    async def get_chat_session(self, session_id: str) -> ChatSession:
        try:
            data = self.redis_client.get(f"chat:{session_id}")
            if data:
                chat_session = ChatSession.model_validate_json(data)
                return chat_session
            return None
        except ConnectionError as e:
            logger.error(f"Redis connection error during get: {e}")
            return None


redis_service = RedisService()