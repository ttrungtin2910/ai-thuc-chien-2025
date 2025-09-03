"""
WebSocket API Routes - Enhanced for Real-time Chat
"""

import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from ..core.security import verify_token
from ..core.websocket_manager import websocket_manager
from ..services.virtual_assistant import virtual_assistant

router = APIRouter(prefix="/websocket", tags=["websocket"])
logger = logging.getLogger(__name__)


@router.get("/status")
async def websocket_status(username: str = Depends(verify_token)):
    """Get WebSocket connection status for the current user"""
    user_sessions = websocket_manager.user_sessions.get(username, set())
    return {
        "connected": len(user_sessions) > 0,
        "session_count": len(user_sessions),
        "sessions": list(user_sessions)
    }


@router.post("/send_message")
async def send_message_via_websocket(
    data: Dict[str, Any],
    username: str = Depends(verify_token)
):
    """Send a chat message via WebSocket to specific user or room"""
    
    try:
        target_user = data.get("target_user")
        room = data.get("room")
        message = data.get("message", {})
        
        if target_user:
            await websocket_manager.send_to_user(target_user, {
                "type": "chat_message",
                "data": message,
                "from": username,
                "timestamp": message.get("timestamp")
            })
            return {"status": "sent", "target": target_user}
        
        elif room:
            await websocket_manager.send_to_room(room, {
                "type": "chat_message", 
                "data": message,
                "from": username,
                "timestamp": message.get("timestamp")
            })
            return {"status": "sent", "target": room}
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Either target_user or room must be specified"
            )
            
    except Exception as e:
        logger.error(f"Error sending WebSocket message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi gửi tin nhắn: {str(e)}"
        )


@router.post("/broadcast_status")
async def broadcast_system_status(
    message: str,
    username: str = Depends(verify_token)
):
    """Broadcast system status message to all connected clients (admin only)"""
    
    try:
        if username != "admin":
            raise HTTPException(
                status_code=403,
                detail="Chỉ admin mới có thể broadcast"
            )
        
        await websocket_manager.broadcast({
            "type": "system_status",
            "message": message,
            "timestamp": str(uuid.uuid4())
        })
        
        return {"status": "broadcasted", "message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error broadcasting status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi broadcast: {str(e)}"
        )
