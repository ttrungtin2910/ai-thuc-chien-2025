"""
Chatbot API Routes - Enhanced with Virtual Assistant and Langraph
"""

import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from ..models.chatbot import ChatMessage, ChatResponse, ChatSessionInfo, ChatHistory
from ..core.security import verify_token
from ..services.virtual_assistant import virtual_assistant

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ChatResponse)
async def chatbot_message(
    message: ChatMessage,
    username: str = Depends(verify_token)
):
    """Send message to virtual assistant and get intelligent response"""
    
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing message for user {username}, session {session_id}")
        
        # Process message through virtual assistant
        response_data = await virtual_assistant.chat(
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
        logger.error(f"Error processing chatbot message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý tin nhắn: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=ChatSessionInfo)
async def get_session_info(
    session_id: str,
    username: str = Depends(verify_token)
):
    """Get information about a chat session"""
    
    try:
        session_info = virtual_assistant.get_session_info(session_id)
        
        return ChatSessionInfo(
            session_id=session_info["session_id"],
            message_count=session_info.get("message_count", 0),
            last_activity=session_info.get("last_activity"),
            recent_messages=session_info.get("recent_messages", []),
            rag_connected=session_info.get("rag_connected", False)
        )
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy thông tin phiên: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(
    session_id: str,
    limit: int = 20,
    username: str = Depends(verify_token)
):
    """Get chat history for a session"""
    
    try:
        # Get conversation history from memory service
        messages = virtual_assistant.memory_service.get_conversation_history(
            session_id=session_id,
            limit=limit
        )
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "type": msg.__class__.__name__,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()  # We can enhance this with actual timestamps
            })
        
        return ChatHistory(
            session_id=session_id,
            messages=formatted_messages,
            total_count=len(formatted_messages)
        )
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy lịch sử trò chuyện: {str(e)}"
        )


@router.post("/session/new")
async def create_new_session(username: str = Depends(verify_token)) -> Dict[str, str]:
    """Create a new chat session"""
    
    try:
        session_id = str(uuid.uuid4())
        
        logger.info(f"Created new chat session {session_id} for user {username}")
        
        return {
            "session_id": session_id,
            "message": "Phiên trò chuyện mới đã được tạo",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating new session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tạo phiên mới: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    username: str = Depends(verify_token)
) -> Dict[str, str]:
    """Delete a chat session and its history"""
    
    try:
        # Note: This is a placeholder. You might want to implement actual session deletion
        # in the conversation memory service
        
        logger.info(f"Session {session_id} deletion requested by user {username}")
        
        return {
            "message": f"Phiên {session_id} đã được đánh dấu để xóa",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xóa phiên: {str(e)}"
        )


@router.get("/sessions")
async def get_user_sessions(username: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get all active sessions for a user"""
    
    try:
        sessions = virtual_assistant.memory_service.get_active_sessions(user_id=username)
        
        return {
            "user_id": username,
            "sessions": sessions,
            "total_count": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy danh sách phiên: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_old_sessions(username: str = Depends(verify_token)) -> Dict[str, str]:
    """Clean up old conversation sessions (admin function)"""
    
    try:
        # Only allow admin users to run cleanup
        if username != "admin":
            raise HTTPException(
                status_code=403,
                detail="Chỉ admin mới có thể thực hiện cleanup"
            )
        
        virtual_assistant.cleanup_old_sessions()
        
        return {
            "message": "Đã dọn dẹp các phiên cũ thành công",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cleanup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi dọn dẹp: {str(e)}"
        )


@router.get("/status")
async def get_chatbot_status(username: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get chatbot service status"""
    
    try:
        # Get RAG service stats
        rag_stats = virtual_assistant.rag_service.get_stats()
        
        return {
            "status": "active",
            "rag_connected": virtual_assistant.rag_connected,
            "memory_connected": virtual_assistant.memory_service.connected,
            "rag_stats": rag_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
