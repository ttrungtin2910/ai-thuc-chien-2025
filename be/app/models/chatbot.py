"""
Chatbot Models

Pydantic models for chatbot interactions.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    timestamp: str
    session_id: Optional[str] = None
