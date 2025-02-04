from openai import AsyncOpenAI
from .config import settings
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"  
        logger.info("LLM Service initialized with OpenAI")

    async def generate_stream(self, messages: list, system_prompt: str) -> AsyncGenerator[str, None]:
        logger.info(f"Generating stream with messages: {messages}, system_prompt: {system_prompt}")

        formatted_messages = self._format_messages(messages, system_prompt)
        logger.info(f"Sending formatted messages to OpenAI: {formatted_messages}")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            stream=True
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _format_messages(self, messages: list, system_prompt: str) -> list:
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
        return formatted_messages

llm_service = LLMService()
