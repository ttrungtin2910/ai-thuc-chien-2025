import asyncio
from typing import Dict, Set
import socketio
from config import Config
import jwt
from datetime import datetime, timedelta

class WebSocketManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",  # Allow all origins for now, can be restricted later
            logger=True,
            engineio_logger=True,
            async_mode='asgi'
        )
        
        # Store user sessions: {user_id: {session_id1, session_id2, ...}}
        self.user_sessions: Dict[str, Set[str]] = {}
        # Store session to user mapping: {session_id: user_id}
        self.session_users: Dict[str, str] = {}
        
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection"""
            print(f"Client connected: {sid}")
            print(f"Auth data: {auth}")
            print(f"Environ: {environ.get('HTTP_ORIGIN', 'No origin')}")
            
            # Very permissive authentication for debugging
            user_id = 'anonymous'  # Default user
            
            try:
                if auth:
                    # Try to get user_id from auth
                    if isinstance(auth, dict) and 'user_id' in auth:
                        user_id = auth['user_id']
                        print(f"User ID from auth: {user_id}")
                    
                    # Try to validate token if provided (but don't fail if invalid)
                    if isinstance(auth, dict) and 'token' in auth and auth['token']:
                        try:
                            token = auth['token']
                            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
                            token_user_id = payload.get('sub')
                            if token_user_id:
                                user_id = token_user_id
                                print(f"Authentication successful for user: {user_id}")
                        except Exception as token_error:
                            print(f"Token validation failed (but allowing connection): {token_error}")
                
                print(f"Final user_id: {user_id}")
                
                # Add session to user mapping
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = set()
                self.user_sessions[user_id].add(sid)
                self.session_users[sid] = user_id
                
                await self.sio.emit('connection_status', {'status': 'connected', 'user_id': user_id}, room=sid)
                print(f"User {user_id} connected with session {sid}")
                
            except Exception as e:
                print(f"Error during connection setup: {e}")
                # Still allow connection with anonymous user
                user_id = 'anonymous'
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = set()
                self.user_sessions[user_id].add(sid)
                self.session_users[sid] = user_id
                
                await self.sio.emit('connection_status', {'status': 'connected', 'user_id': user_id}, room=sid)
                print(f"Anonymous user connected with session {sid}")
            
            return True  # Always allow connection
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            print(f"Client disconnected: {sid}")
            
            # Remove session from mappings
            if sid in self.session_users:
                user_id = self.session_users[sid]
                self.user_sessions[user_id].discard(sid)
                
                # Remove user mapping if no sessions left
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]
                
                del self.session_users[sid]
                print(f"User {user_id} disconnected session {sid}")
        
        @self.sio.event
        async def join_room(sid, data):
            """Handle joining a room"""
            room = data.get('room')
            if room:
                await self.sio.enter_room(sid, room)
                await self.sio.emit('room_joined', {'room': room}, room=sid)
                print(f"Session {sid} joined room {room}")
        
        @self.sio.event
        async def leave_room(sid, data):
            """Handle leaving a room"""
            room = data.get('room')
            if room:
                await self.sio.leave_room(sid, room)
                await self.sio.emit('room_left', {'room': room}, room=sid)
                print(f"Session {sid} left room {room}")
        
        @self.sio.event
        async def ping(sid, data):
            """Handle ping from client"""
            await self.sio.emit('pong', {'timestamp': data.get('timestamp')}, room=sid)
    
    async def send_to_user(self, user_id: str, data: dict):
        """Send message to all sessions of a specific user"""
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                try:
                    await self.sio.emit('message', data, room=session_id)
                except Exception as e:
                    print(f"Error sending message to session {session_id}: {e}")
    
    async def send_to_room(self, room: str, data: dict):
        """Send message to a specific room"""
        try:
            await self.sio.emit('message', data, room=room)
        except Exception as e:
            print(f"Error sending message to room {room}: {e}")
    
    async def broadcast(self, data: dict):
        """Broadcast message to all connected clients"""
        try:
            await self.sio.emit('broadcast', data)
        except Exception as e:
            print(f"Error broadcasting message: {e}")
    
    def get_sio(self):
        """Get the Socket.IO server instance"""
        return self.sio

# Global instance
websocket_manager = WebSocketManager()

