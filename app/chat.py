from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatSession(BaseModel):
    session_id: str
    messages: List[Message]
    system_prompt: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None