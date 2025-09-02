"""
Chatbot API Routes
"""

from datetime import datetime
from fastapi import APIRouter, Depends

from ..models.chatbot import ChatMessage, ChatResponse
from ..core.security import verify_token

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/message", response_model=ChatResponse)
async def chatbot_message(
    message: ChatMessage,
    username: str = Depends(verify_token)
):
    """Send message to chatbot and get response"""
    # Integrate with RAG service for intelligent responses
    
    return ChatResponse(
        response="Đây là phản hồi mẫu từ chatbot. Tính năng này sẽ được phát triển thêm trong tương lai.",
        timestamp=datetime.now().isoformat(),
        session_id=message.session_id
    )
