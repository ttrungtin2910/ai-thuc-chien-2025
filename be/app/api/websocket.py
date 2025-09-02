"""
WebSocket API Routes
"""

from fastapi import APIRouter, Depends

from ..core.security import verify_token
from ..core.websocket import websocket_manager

router = APIRouter(prefix="/websocket", tags=["websocket"])


@router.get("/status")
async def websocket_status(username: str = Depends(verify_token)):
    """Get WebSocket connection status for the current user"""
    user_sessions = websocket_manager.user_sessions.get(username, set())
    return {
        "connected": len(user_sessions) > 0,
        "session_count": len(user_sessions),
        "sessions": list(user_sessions)
    }
