import uuid
from .chat import ChatSession, Message, ChatRequest
from typing import AsyncGenerator
from .redis_service import redis_service
from .llm_service import llm_service
import logging
from .postgres_service import postgres_service
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatService:
    async def create_or_continue_chat(self, chat_request: ChatRequest, system_prompt:str ="You are a helpful AI assistant. Reply to anything with I love you then the reponse.") -> AsyncGenerator[str, None]:
        session_id = chat_request.session_id or str(uuid.uuid4())
        logger.info(f"Creating/continuing chat session: {session_id}")
        
        yield {"session_id": session_id}

        # Get or create chat session
        try:  
            chat_session = await redis_service.get_chat_session(session_id)
            logger.info(f"Retrieved chat session: {chat_session}")
        except Exception as e:
            logger.error(f"Failed to retrieve chat session: {e}")
            return

        if not chat_session:
            chat_session = ChatSession(
                session_id=session_id,
                messages=[],
                system_prompt=system_prompt
            )
            logger.info(f"Created new chat session: {chat_session}")
        
        # Save the latest system prompt
        chat_session.system_prompt = system_prompt

        # Add user message
        chat_session.messages.append(
            Message(role="user", content=chat_request.message)
        )

        # Get response from LLM
        full_response = ""
        async for chunk in llm_service.generate_stream(chat_session.messages, chat_session.system_prompt):
            full_response += chunk  
            yield chunk

        # Add assistant's response to history
        chat_session.messages.append(
            Message(role="assistant", content=full_response)
        )

        # Save updated session
        await redis_service.save_chat_session(chat_session)
        logger.info(f"Saved chat session: {chat_session}")

    async def flush_session_to_postgres(self, session_id: str):
        chat_session = await redis_service.get_chat_session(session_id)
        if chat_session:
            last_request_timestamp = datetime.now().isoformat()
            flushed_timestamp = datetime.now().isoformat()
            summary = " -- ".join([msg.content for msg in chat_session.messages])
            postgres_service.flush_session(session_id, last_request_timestamp, flushed_timestamp, summary)

chat_service = ChatService()