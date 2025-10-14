import asyncio
from typing import Dict, Set
import socketio
from .config import Config
import jwt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",  # Allow all origins for development/flexibility
            async_mode="asgi",
            logger=True,
            engineio_logger=True,
        )

        # Store user sessions: {user_id: {session_id1, session_id2, ...}}
        self.user_sessions: Dict[str, Set[str]] = {}
        # Store session to user mapping: {session_id: user_id}
        self.session_users: Dict[str, str] = {}

        self.setup_event_handlers()

    def setup_event_handlers(self):
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection - always accepts connections"""
            user_id = "anonymous"  # Default user

            try:
                logger.info(f"Client connection attempt: {sid}")
                logger.info(f"Auth data: {auth}")
                logger.info(
                    f"Environ keys: {list(environ.keys()) if environ else 'None'}"
                )

                if auth:
                    # Try to get user_id from auth
                    if isinstance(auth, dict) and "user_id" in auth:
                        user_id = auth["user_id"]
                        logger.info(f"User ID from auth: {user_id}")

                    # Try to validate token if provided
                    if isinstance(auth, dict) and "token" in auth and auth["token"]:
                        try:
                            token = auth["token"]
                            payload = jwt.decode(
                                token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM]
                            )
                            token_user_id = payload.get("sub")
                            if token_user_id:
                                user_id = token_user_id
                                logger.info(
                                    f"Token authentication successful for user: {user_id}"
                                )
                        except jwt.ExpiredSignatureError:
                            logger.warning(f"Token expired for user: {user_id}")
                        except jwt.InvalidTokenError as token_error:
                            logger.warning(f"Invalid token: {token_error}")
                        except Exception as token_error:
                            logger.warning(f"Token validation error: {token_error}")

                # Add session to user mapping
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = set()
                self.user_sessions[user_id].add(sid)
                self.session_users[sid] = user_id

                # Automatically join user room
                await self.sio.enter_room(sid, f"user_{user_id}")

                # Send connection confirmation
                await self.sio.emit(
                    "connection_status",
                    {"status": "connected", "user_id": user_id},
                    room=sid,
                )
                await self.sio.emit(
                    "joined_room",
                    {"message": f"Joined room for user {user_id}", "username": user_id},
                    room=sid,
                )

                logger.info(
                    f"✓ User '{user_id}' connected successfully with session {sid}"
                )

            except Exception as e:
                logger.error(f"Error during connection setup: {e}", exc_info=True)
                # Still allow connection with anonymous user even on error
                try:
                    if user_id not in self.user_sessions:
                        self.user_sessions[user_id] = set()
                    self.user_sessions[user_id].add(sid)
                    self.session_users[sid] = user_id

                    await self.sio.enter_room(sid, f"user_{user_id}")
                    await self.sio.emit(
                        "connection_status",
                        {"status": "connected", "user_id": user_id},
                        room=sid,
                    )
                    logger.info(
                        f"✓ Fallback: User '{user_id}' connected with session {sid}"
                    )
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback connection setup failed: {fallback_error}",
                        exc_info=True,
                    )

            # ALWAYS return True to accept the connection
            logger.info(f"Returning True for connection {sid}")
            return True

        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {sid}")

            # Remove session from mappings
            if sid in self.session_users:
                user_id = self.session_users[sid]
                self.user_sessions[user_id].discard(sid)

                # Remove user mapping if no sessions left
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]

                del self.session_users[sid]
                logger.info(f"User {user_id} disconnected session {sid}")

        @self.sio.event
        async def join_room(sid, data):
            """Handle joining a room"""
            room = data.get("room")
            if room:
                await self.sio.enter_room(sid, room)
                await self.sio.emit("room_joined", {"room": room}, room=sid)
                logger.debug(f"Session {sid} joined room {room}")

        @self.sio.event
        async def leave_room(sid, data):
            """Handle leaving a room"""
            room = data.get("room")
            if room:
                await self.sio.leave_room(sid, room)
                await self.sio.emit("room_left", {"room": room}, room=sid)
                logger.debug(f"Session {sid} left room {room}")

        @self.sio.event
        async def ping(sid, data):
            """Handle ping from client"""
            await self.sio.emit("pong", {"timestamp": data.get("timestamp")}, room=sid)

        @self.sio.event
        async def chat_message(sid, data):
            """Handle real-time chat message"""
            try:
                user_id = self.session_users.get(sid, "anonymous")
                message = data.get("message", "")
                session_id = data.get("session_id")

                if not message.strip():
                    await self.sio.emit(
                        "error", {"message": "Tin nhắn không được rỗng"}, room=sid
                    )
                    return

                # Generate session ID if not provided
                if not session_id:
                    session_id = f"ws_{user_id}_{sid}"

                logger.info(f"Processing real-time chat message from {user_id}")

                # Import here to avoid circular imports
                from ..services.virtual_assistant import virtual_assistant

                # Send typing indicator
                await self.sio.emit(
                    "typing", {"session_id": session_id, "typing": True}, room=sid
                )

                # Process message through virtual assistant
                response_data = await virtual_assistant.chat(
                    message=message, session_id=session_id, user_id=user_id
                )

                # Stop typing indicator
                await self.sio.emit(
                    "typing", {"session_id": session_id, "typing": False}, room=sid
                )

                # Send response back to client
                await self.sio.emit(
                    "chat_response",
                    {
                        "session_id": session_id,
                        "response": response_data["response"],
                        "timestamp": response_data["timestamp"],
                        "metadata": response_data.get("metadata", {}),
                    },
                    room=sid,
                )

                logger.debug(f"Chat response sent to {user_id}")

            except Exception as e:
                logger.error(f"Error processing chat message: {e}")
                await self.sio.emit(
                    "error",
                    {
                        "message": f"Lỗi xử lý tin nhắn: {str(e)}",
                        "session_id": data.get("session_id"),
                    },
                    room=sid,
                )

        @self.sio.event
        async def join_chat_session(sid, data):
            """Join a specific chat session room"""
            try:
                session_id = data.get("session_id")
                if session_id:
                    room_name = f"chat_{session_id}"
                    await self.sio.enter_room(sid, room_name)
                    await self.sio.emit(
                        "session_joined",
                        {"session_id": session_id, "room": room_name},
                        room=sid,
                    )
                    logger.debug(f"Session {sid} joined chat session {session_id}")
            except Exception as e:
                logger.error(f"Error joining chat session: {e}")
                await self.sio.emit(
                    "error", {"message": f"Lỗi tham gia phiên chat: {str(e)}"}, room=sid
                )

        @self.sio.event
        async def leave_chat_session(sid, data):
            """Leave a specific chat session room"""
            try:
                session_id = data.get("session_id")
                if session_id:
                    room_name = f"chat_{session_id}"
                    await self.sio.leave_room(sid, room_name)
                    await self.sio.emit(
                        "session_left",
                        {"session_id": session_id, "room": room_name},
                        room=sid,
                    )
                    logger.debug(f"Session {sid} left chat session {session_id}")
            except Exception as e:
                logger.error(f"Error leaving chat session: {e}")

        @self.sio.event
        async def get_chat_history(sid, data):
            """Get chat history for a session via WebSocket"""
            try:
                session_id = data.get("session_id")
                limit = data.get("limit", 20)

                if not session_id:
                    await self.sio.emit(
                        "error", {"message": "Session ID required"}, room=sid
                    )
                    return

                # Import here to avoid circular imports
                from ..services.virtual_assistant import virtual_assistant

                # Get conversation history
                messages = virtual_assistant.memory_service.get_conversation_history(
                    session_id=session_id, limit=limit
                )

                # Format messages
                formatted_messages = []
                for msg in messages:
                    formatted_messages.append(
                        {
                            "type": msg.__class__.__name__,
                            "content": msg.content,
                            "timestamp": str(
                                msg
                            ),  # Can be enhanced with actual timestamps
                        }
                    )

                await self.sio.emit(
                    "chat_history",
                    {
                        "session_id": session_id,
                        "messages": formatted_messages,
                        "total_count": len(formatted_messages),
                    },
                    room=sid,
                )

            except Exception as e:
                logger.error(f"Error getting chat history: {e}")
                await self.sio.emit(
                    "error",
                    {
                        "message": f"Lỗi lấy lịch sử chat: {str(e)}",
                        "session_id": data.get("session_id"),
                    },
                    room=sid,
                )

    async def send_to_user(self, user_id: str, data: dict):
        """Send message to all sessions of a specific user"""
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                try:
                    await self.sio.emit("message", data, room=session_id)
                except Exception as e:
                    logger.error(f"Error sending message to session {session_id}: {e}")

    async def send_to_room(self, room: str, data: dict):
        """Send message to a specific room"""
        try:
            await self.sio.emit("message", data, room=room)
        except Exception as e:
            logger.error(f"Error sending message to room {room}: {e}")

    async def broadcast(self, data: dict):
        """Broadcast message to all connected clients"""
        try:
            await self.sio.emit("broadcast", data)
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    def get_sio(self):
        """Get the Socket.IO server instance"""
        return self.sio


# Global instance
websocket_manager = WebSocketManager()
