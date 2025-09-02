"""
WebSocket Management

WebSocket connection and message handling.
"""

import socketio
import logging
from typing import Set, Dict

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        """Initialize WebSocket manager with Socket.IO"""
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            logger=False,
            engineio_logger=False
        )
        
        # Track user sessions: {username: set(session_ids)}
        self.user_sessions: Dict[str, Set[str]] = {}
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            logger.info(f"WebSocket client connected: {sid}")
            # Send welcome message
            await self.sio.emit('connected', {'message': 'Connected to DVC.AI server'}, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            logger.info(f"WebSocket client disconnected: {sid}")
            # Remove from user sessions
            for username, sessions in self.user_sessions.items():
                if sid in sessions:
                    sessions.discard(sid)
                    logger.info(f"Removed session {sid} from user {username}")
                    break
        
        @self.sio.event
        async def join_user_room(sid, data):
            """Join user-specific room for targeted messages"""
            username = data.get('username')
            if username:
                if username not in self.user_sessions:
                    self.user_sessions[username] = set()
                
                self.user_sessions[username].add(sid)
                await self.sio.enter_room(sid, f"user_{username}")
                logger.info(f"User {username} joined room with session {sid}")
                
                await self.sio.emit('joined_room', {
                    'message': f'Joined room for user {username}',
                    'username': username
                }, room=sid)
    
    async def send_to_user(self, username: str, event: str, data: dict):
        """Send message to specific user"""
        room = f"user_{username}"
        await self.sio.emit(event, data, room=room)
        logger.info(f"Sent {event} to user {username}: {data}")
    
    async def broadcast(self, event: str, data: dict):
        """Broadcast message to all connected clients"""
        await self.sio.emit(event, data)
        logger.info(f"Broadcasted {event}: {data}")
    
    async def send_upload_progress(self, username: str, task_id: str, progress: int, filename: str):
        """Send file upload progress to user"""
        await self.send_to_user(username, 'file_upload_progress', {
            'task_id': task_id,
            'progress': progress,
            'filename': filename,
            'message': f'Uploading {filename}... {progress}%'
        })
    
    async def send_upload_complete(self, username: str, task_id: str, filename: str, success: bool = True, error: str = None):
        """Send file upload completion notification"""
        await self.send_to_user(username, 'file_upload_complete', {
            'task_id': task_id,
            'filename': filename,
            'success': success,
            'error': error,
            'message': f'Upload {"completed" if success else "failed"}: {filename}'
        })
    
    async def send_bulk_upload_progress(self, username: str, bulk_task_id: str, completed: int, total: int, current_file: str = None):
        """Send bulk upload progress to user"""
        progress = int((completed / total) * 100) if total > 0 else 0
        await self.send_to_user(username, 'bulk_upload_progress', {
            'bulk_task_id': bulk_task_id,
            'completed': completed,
            'total': total,
            'progress': progress,
            'current_file': current_file,
            'message': f'Processing {completed}/{total} files... {progress}%'
        })


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
