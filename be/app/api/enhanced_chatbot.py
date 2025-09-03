"""
Enhanced Chatbot API Routes - Using Advanced Agent Architecture
"""

import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from ..models.chatbot import ChatMessage, ChatResponse, ChatSessionInfo, ChatHistory
from ..core.security import verify_token
from ..services.enhanced_virtual_assistant import enhanced_virtual_assistant

router = APIRouter(prefix="/enhanced-chatbot", tags=["enhanced-chatbot"])
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ChatResponse)
async def enhanced_chatbot_message(
    message: ChatMessage,
    username: str = Depends(verify_token)
):
    """Send message to enhanced virtual assistant and get intelligent response"""
    
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing enhanced message for user {username}, session {session_id}")
        
        # Process message through enhanced virtual assistant
        response_data = await enhanced_virtual_assistant.chat(
            message=message.message,
            session_id=session_id,
            user_id=username
        )
        
        return ChatResponse(
            response=response_data["response"],
            timestamp=response_data["timestamp"],
            session_id=response_data["session_id"],
            metadata=response_data.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error processing enhanced chatbot message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý tin nhắn: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=ChatSessionInfo)
async def get_enhanced_session_info(
    session_id: str,
    username: str = Depends(verify_token)
):
    """Get information about an enhanced chat session"""
    
    try:
        session_info = enhanced_virtual_assistant.get_session_info(session_id)
        
        return ChatSessionInfo(
            session_id=session_info["session_id"],
            message_count=session_info.get("message_count", 0),
            last_activity=session_info.get("last_activity"),
            recent_messages=session_info.get("recent_messages", []),
            rag_connected=session_info.get("connected", False)
        )
        
    except Exception as e:
        logger.error(f"Error getting enhanced session info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy thông tin phiên: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_enhanced_chat_history(
    session_id: str,
    limit: int = 20,
    username: str = Depends(verify_token)
):
    """Get chat history for an enhanced session"""
    
    try:
        # Get conversation history from memory service
        messages = enhanced_virtual_assistant.memory_service.get_conversation_history(
            session_id=session_id,
            limit=limit
        )
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "type": msg.__class__.__name__,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()  # Could be enhanced with actual timestamps
            })
        
        return ChatHistory(
            session_id=session_id,
            messages=formatted_messages,
            total_count=len(formatted_messages)
        )
        
    except Exception as e:
        logger.error(f"Error getting enhanced chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy lịch sử trò chuyện: {str(e)}"
        )


@router.get("/status")
async def get_enhanced_chatbot_status(username: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get enhanced chatbot service status"""
    
    try:
        return enhanced_virtual_assistant.get_service_status()
        
    except Exception as e:
        logger.error(f"Error getting enhanced status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/session/new")
async def create_enhanced_session(username: str = Depends(verify_token)) -> Dict[str, str]:
    """Create a new enhanced chat session"""
    
    try:
        session_id = str(uuid.uuid4())
        
        logger.info(f"Created new enhanced chat session {session_id} for user {username}")
        
        return {
            "session_id": session_id,
            "message": "Phiên trò chuyện nâng cao mới đã được tạo",
            "agent_type": "enhanced",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating enhanced session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tạo phiên mới: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_enhanced_sessions(username: str = Depends(verify_token)) -> Dict[str, str]:
    """Clean up old enhanced conversation sessions (admin function)"""
    
    try:
        # Only allow admin users to run cleanup
        if username != "admin":
            raise HTTPException(
                status_code=403,
                detail="Chỉ admin mới có thể thực hiện cleanup"
            )
        
        enhanced_virtual_assistant.cleanup_old_sessions()
        
        return {
            "message": "Đã dọn dẹp các phiên nâng cao thành công",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced cleanup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi dọn dẹp: {str(e)}"
        )
