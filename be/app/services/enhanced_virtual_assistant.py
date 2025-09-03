"""
Enhanced Virtual Assistant Service using Advanced Agent Architecture
Modular RAG and Conversational AI with LangGraph
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage

from ..agent.graph_builder import MainGraphBuilder
from ..agent.state import InputState
from ..agent.configuration import Configuration
from .conversation_memory import conversation_memory

logger = logging.getLogger(__name__)


class EnhancedVirtualAssistantService:
    """Enhanced Virtual Assistant with modular agent architecture."""
    
    def __init__(self):
        """Initialize Enhanced Virtual Assistant."""
        
        # Initialize memory service
        self.memory_service = conversation_memory
        
        # Initialize graph builder
        self.graph_builder = MainGraphBuilder()
        self.workflow = self.graph_builder.compile_graph()
        
        # Connection status
        self.connected = True
        
        logger.info("Enhanced Virtual Assistant initialized successfully")
    
    async def chat(self, message: str, session_id: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Main chat interface using advanced agent workflow.
        
        Args:
            message: User message
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Chat response with metadata
        """
        
        try:
            # Get conversation history for context
            history = self.memory_service.get_conversation_history(session_id, limit=8)
            
            # Get session context/memories
            session_context = self.memory_service.get_session_context(session_id)
            memories = session_context.get("memories", {})
            
            # Create input state
            input_state = InputState(
                messages=[*history, HumanMessage(content=message)],
                session_id=session_id,
                user_id=user_id,
                memories=memories
            )
            
            # Create configuration with thread_id
            config = {
                "configurable": {
                    **Configuration().__dict__,
                    "thread_id": session_id  # Add thread_id for LangGraph checkpointer
                }
            }
            
            # Run the agent workflow
            logger.info(f"Processing message for user {user_id}, session {session_id}")
            final_state = await self.workflow.ainvoke(input_state, config=config)
            
            # Extract AI response
            ai_response = None
            if final_state.get("messages"):
                ai_response = final_state["messages"][-1]
            
            if not ai_response or not isinstance(ai_response, AIMessage):
                return {
                    "response": "Xin lỗi, có lỗi xảy ra trong quá trình xử lý.",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"error": "No AI response generated"}
                }
            
            # Save conversation to memory
            await self._save_conversation(
                session_id=session_id,
                user_id=user_id,
                user_message=HumanMessage(content=message),
                ai_message=ai_response
            )
            
            # Prepare response with metadata
            response_data = {
                "response": ai_response.content,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "rag_used": ai_response.additional_kwargs.get("rag_used", False),
                    "confidence": ai_response.additional_kwargs.get("confidence", 0.0),
                    "extracted_entities": ai_response.additional_kwargs.get("extracted_entities", []),
                    "source_info": ai_response.additional_kwargs.get("source_info", ""),
                    "response_type": ai_response.additional_kwargs.get("response_type", "unknown"),
                    "conversation_length": len(final_state.get("messages", []))
                }
            }
            
            logger.info(f"Chat completed successfully for session {session_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "response": f"Xin lỗi, có lỗi xảy ra: {str(e)}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"error": str(e)}
            }
    
    async def _save_conversation(
        self, 
        session_id: str, 
        user_id: str, 
        user_message: HumanMessage, 
        ai_message: AIMessage
    ):
        """Save conversation messages to memory."""
        
        try:
            # Prepare metadata
            metadata = {
                "rag_used": ai_message.additional_kwargs.get("rag_used", False),
                "confidence": ai_message.additional_kwargs.get("confidence", 0.0),
                "sources_count": len(ai_message.additional_kwargs.get("extracted_entities", [])),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save user message
            self.memory_service.save_message(
                session_id=session_id,
                user_id=user_id,
                message=user_message,
                metadata=metadata
            )
            
            # Save AI message
            self.memory_service.save_message(
                session_id=session_id,
                user_id=user_id,
                message=ai_message,
                metadata=metadata
            )
            
            logger.info(f"Saved conversation for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information and context."""
        
        try:
            context = self.memory_service.get_session_context(session_id)
            history = self.memory_service.get_conversation_history(session_id, limit=5)
            
            return {
                "session_id": session_id,
                "message_count": context.get("message_count", 0),
                "last_activity": context.get("last_activity"),
                "recent_messages": [
                    {
                        "type": msg.__class__.__name__,
                        "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    }
                    for msg in history[-3:]  # Last 3 messages
                ],
                "connected": self.connected,
                "agent_type": "enhanced"
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {
                "session_id": session_id,
                "error": str(e)
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and health information."""
        
        try:
            return {
                "service": "enhanced_virtual_assistant",
                "status": "active" if self.connected else "error",
                "agent_architecture": "modular_langgraph",
                "rag_enabled": True,
                "memory_connected": self.memory_service.connected,
                "features": [
                    "intelligent_routing",
                    "context_aware_rag",
                    "citation_support", 
                    "conversation_memory",
                    "query_transformation"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                "service": "enhanced_virtual_assistant",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup_old_sessions(self):
        """Clean up old conversation sessions."""
        try:
            self.memory_service.cleanup_old_sessions()
            logger.info("Cleaned up old conversation sessions")
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")


# Global instance
enhanced_virtual_assistant = EnhancedVirtualAssistantService()
