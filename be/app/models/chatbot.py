"""
Chatbot Models

Pydantic models for chatbot interactions with Virtual Assistant.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    timestamp: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSessionInfo(BaseModel):
    session_id: str
    message_count: int
    last_activity: Optional[datetime] = None
    recent_messages: List[Dict[str, Any]] = []
    rag_connected: bool = False


class ChatHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    total_count: int


class ConversationMessage(BaseModel):
    type: str  # HumanMessage or AIMessage
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class SessionStatus(BaseModel):
    status: str
    rag_connected: bool = False
    memory_connected: bool = False
    rag_stats: Optional[Dict[str, Any]] = None
    timestamp: str
