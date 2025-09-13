"""
Conversation Memory Service for Virtual Assistant
Manages conversation history and context using MongoDB
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from ..core.config import Config

logger = logging.getLogger(__name__)

class ConversationMemoryService:
    def __init__(self, mongodb_url: str = None, db_name: str = None):
        """
        Initialize conversation memory service
        
        Args:
            mongodb_url: MongoDB connection URL (defaults to Config.MONGODB_URL)
            db_name: Database name (defaults to Config.MONGODB_DATABASE)
        """
        self.mongodb_url = mongodb_url or Config.MONGODB_URL
        self.db_name = db_name or Config.MONGODB_DATABASE
        self.collection_name = "conversations"
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        
        # Memory configuration
        self.max_messages_per_session = 50  # Limit messages per session
        self.session_timeout_hours = 24     # Sessions expire after 24h
        
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_url, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            self.connected = True
            
            # Create indexes for performance
            self.collection.create_index("session_id")
            self.collection.create_index("user_id")
            self.collection.create_index("timestamp")
            
            logger.info("Connected to MongoDB for conversation memory")
            
        except ConnectionFailure as e:
            logger.warning(f"Failed to connect to MongoDB: {e}. Using in-memory storage.")
            self.connected = False
            # Fallback to in-memory storage
            self._memory_store = {}
    
    def save_message(self, session_id: str, user_id: str, message: BaseMessage, metadata: Optional[Dict] = None):
        """
        Save a message to conversation history
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            message: The message to save (HumanMessage or AIMessage)
            metadata: Additional metadata
        """
        try:
            message_data = {
                "session_id": session_id,
                "user_id": user_id,
                "message_type": message.__class__.__name__,
                "content": message.content,
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            if self.connected:
                # Save to MongoDB
                self.collection.insert_one(message_data)
            else:
                # Save to in-memory store
                if session_id not in self._memory_store:
                    self._memory_store[session_id] = []
                self._memory_store[session_id].append(message_data)
                
                # Limit memory usage
                if len(self._memory_store[session_id]) > self.max_messages_per_session:
                    self._memory_store[session_id] = self._memory_store[session_id][-self.max_messages_per_session:]
            
            logger.debug(f"Saved message for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[BaseMessage]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in chronological order
        """
        try:
            if self.connected:
                # Get from MongoDB
                cursor = self.collection.find(
                    {"session_id": session_id}
                ).sort("timestamp", 1).limit(limit)
                messages_data = list(cursor)
            else:
                # Get from in-memory store
                messages_data = self._memory_store.get(session_id, [])[-limit:]
            
            # Convert to LangChain messages
            messages = []
            for msg_data in messages_data:
                if msg_data["message_type"] == "HumanMessage":
                    messages.append(HumanMessage(content=msg_data["content"]))
                elif msg_data["message_type"] == "AIMessage":
                    messages.append(AIMessage(content=msg_data["content"]))
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get session context and metadata
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session context dictionary
        """
        try:
            if self.connected:
                # Get latest message with metadata
                latest_msg = self.collection.find_one(
                    {"session_id": session_id},
                    sort=[("timestamp", -1)]
                )
                
                if latest_msg:
                    return {
                        "session_id": session_id,
                        "last_activity": latest_msg["timestamp"],
                        "message_count": self.collection.count_documents({"session_id": session_id}),
                        "metadata": latest_msg.get("metadata", {})
                    }
            else:
                # Get from in-memory store
                messages = self._memory_store.get(session_id, [])
                if messages:
                    return {
                        "session_id": session_id,
                        "last_activity": messages[-1]["timestamp"],
                        "message_count": len(messages),
                        "metadata": messages[-1].get("metadata", {})
                    }
            
            return {"session_id": session_id, "message_count": 0}
            
        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            return {"session_id": session_id, "message_count": 0}
    
    def cleanup_old_sessions(self):
        """Clean up old sessions based on timeout"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)
            
            if self.connected:
                # Delete from MongoDB
                result = self.collection.delete_many({"timestamp": {"$lt": cutoff_time}})
                logger.info(f"Cleaned up {result.deleted_count} old messages")
            else:
                # Clean up in-memory store
                sessions_to_remove = []
                for session_id, messages in self._memory_store.items():
                    # Remove old messages
                    recent_messages = [
                        msg for msg in messages 
                        if msg["timestamp"] > cutoff_time
                    ]
                    
                    if recent_messages:
                        self._memory_store[session_id] = recent_messages
                    else:
                        sessions_to_remove.append(session_id)
                
                # Remove empty sessions
                for session_id in sessions_to_remove:
                    del self._memory_store[session_id]
                
                logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
    
    def get_active_sessions(self, user_id: Optional[str] = None) -> List[Dict]:
        """
        Get list of active sessions
        
        Args:
            user_id: Filter by user ID (optional)
            
        Returns:
            List of active session information
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)
            
            if self.connected:
                # Query MongoDB
                filter_query = {"timestamp": {"$gte": cutoff_time}}
                if user_id:
                    filter_query["user_id"] = user_id
                
                pipeline = [
                    {"$match": filter_query},
                    {"$group": {
                        "_id": "$session_id",
                        "user_id": {"$first": "$user_id"},
                        "last_activity": {"$max": "$timestamp"},
                        "message_count": {"$sum": 1}
                    }}
                ]
                
                sessions = list(self.collection.aggregate(pipeline))
                return [
                    {
                        "session_id": session["_id"],
                        "user_id": session["user_id"],
                        "last_activity": session["last_activity"],
                        "message_count": session["message_count"]
                    }
                    for session in sessions
                ]
            else:
                # Get from in-memory store
                sessions = []
                for session_id, messages in self._memory_store.items():
                    if messages and messages[-1]["timestamp"] > cutoff_time:
                        if not user_id or messages[0].get("user_id") == user_id:
                            sessions.append({
                                "session_id": session_id,
                                "user_id": messages[0].get("user_id"),
                                "last_activity": messages[-1]["timestamp"],
                                "message_count": len(messages)
                            })
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []
    
    def create_session_summary(self, session_id: str) -> str:
        """
        Create a summary of the conversation session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Text summary of the conversation
        """
        try:
            messages = self.get_conversation_history(session_id, limit=50)
            
            if not messages:
                return "Không có lịch sử cuộc trò chuyện."
            
            # Create a simple summary
            human_messages = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
            ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]
            
            summary = f"""
Tóm tắt cuộc trò chuyện:
- Số tin nhắn của người dùng: {len(human_messages)}
- Số phản hồi của AI: {len(ai_messages)}
- Chủ đề chính: {', '.join(human_messages[:3]) if human_messages else 'Chưa có câu hỏi'}
"""
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Failed to create session summary: {e}")
            return "Không thể tạo tóm tắt cuộc trò chuyện."

# Global instance
conversation_memory = ConversationMemoryService()
