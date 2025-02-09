from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from .chat import ChatRequest
from .chat_service import chat_service
import logging
import asyncio
import json

logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot API")

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    logger.info(f"Received chat request: {chat_request}")
    
    async def event_generator():
        try:
            session_id = None
            async for chunk in chat_service.create_or_continue_chat(chat_request):
                if chunk:
                    # Capture the session_id from the first yielded message
                    if isinstance(chunk, dict) and "session_id" in chunk:
                        session_id = chunk["session_id"]
                    # Convert chunk to JSON string if it's a dict
                    if isinstance(chunk, dict):
                        data = json.dumps(chunk)
                    else:
                        data = chunk

                    yield {
                        "event": "message",
                        "data": data
                    }
                await asyncio.sleep(0.01)
        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
        finally:
            await chat_service.flush_session_to_postgres(session_id)

    return EventSourceResponse(
        event_generator(), 
        media_type="text/event-stream"
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)