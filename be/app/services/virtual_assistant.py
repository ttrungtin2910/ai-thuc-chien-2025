"""
Virtual Assistant Service with Langraph
Advanced conversational AI with memory, RAG and workflow management
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from .rag_service import RAGService
from .conversation_memory import conversation_memory
from ..core.config import Config

logger = logging.getLogger(__name__)

# State definition for Langraph using TypedDict
class AssistantState(TypedDict):
    messages: List[BaseMessage]
    session_id: str
    user_id: str
    context: Dict[str, Any]
    rag_results: Optional[Dict[str, Any]]
    needs_search: bool
    conversation_summary: str

class VirtualAssistantService:
    def __init__(self):
        """Initialize Virtual Assistant with Langraph workflow"""
        
        # Initialize services
        self.rag_service = RAGService()
        self.memory_service = conversation_memory
        
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model=Config.OPENAI_CHAT_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        
        # Initialize RAG connection
        self.rag_connected = False
        
        # Create Langraph workflow
        self.workflow = self._create_workflow()
        
        # System prompt for the assistant
        self.system_prompt = """Bạn là DVC.AI, một trợ lý ảo thông minh chuyên về dịch vụ công và thủ tục hành chính Việt Nam.

Tính cách và phong cách:
- Thân thiện, chuyên nghiệp và luôn sẵn sàng hỗ trợ
- Sử dụng tiếng Việt tự nhiên, dễ hiểu
- Kiên nhẫn và chi tiết trong giải thích
- Luôn cập nhật thông tin chính xác

Khả năng:
- Tìm kiếm thông tin từ cơ sở dữ liệu thủ tục hành chính
- Hướng dẫn chi tiết các quy trình, thủ tục
- Tư vấn về giấy tờ cần thiết và cách thức thực hiện
- Ghi nhớ ngữ cảnh cuộc trò chuyện để hỗ trợ tốt hơn

Quy tắc:
1. Luôn sử dụng thông tin từ cơ sở dữ liệu để trả lời
2. Nếu không tìm thấy thông tin, hãy thành thật nói rằng cần tìm hiểu thêm
3. Cung cấp thông tin từng bước rõ ràng
4. Hỏi lại nếu câu hỏi chưa rõ ràng
5. Đề xuất các câu hỏi liên quan để hỗ trợ tốt hơn"""
    
    def _create_workflow(self) -> StateGraph:
        """Create Langraph workflow for conversation management"""
        
        # Create workflow graph
        workflow = StateGraph(AssistantState)
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("search_knowledge", self._search_knowledge) 
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("save_context", self._save_context)
        
        # Define edges
        workflow.set_entry_point("analyze_query")
        
        workflow.add_conditional_edges(
            "analyze_query",
            self._should_search,
            {
                "search": "search_knowledge",
                "direct": "generate_response"
            }
        )
        
        workflow.add_edge("search_knowledge", "generate_response")
        workflow.add_edge("generate_response", "save_context")
        workflow.add_edge("save_context", END)
        
        return workflow.compile()
    
    def _analyze_query(self, state: AssistantState) -> AssistantState:
        """Analyze user query to determine if RAG search is needed"""
        
        try:
            # Get the latest user message
            user_message = state["messages"][-1] if state["messages"] else None
            
            if not user_message or not isinstance(user_message, HumanMessage):
                state["needs_search"] = False
                return state
            
            query = user_message.content.lower()
            
            # Keywords that typically require knowledge search
            search_keywords = [
                'thủ tục', 'hồ sơ', 'giấy tờ', 'đăng ký', 'cấp', 'làm',
                'xin', 'nộp', 'phí', 'lệ phí', 'thời gian', 'quy trình',
                'bao lâu', 'ở đâu', 'như thế nào', 'cần gì', 'yêu cầu'
            ]
            
            # Check if query contains search keywords
            needs_search = any(keyword in query for keyword in search_keywords)
            
            # Also search if query is a question
            question_indicators = ['?', 'như thế nào', 'ra sao', 'thế nào']
            if any(indicator in query for indicator in question_indicators):
                needs_search = True
            
            state["needs_search"] = needs_search
            
            logger.info(f"Query analysis: needs_search = {needs_search}")
            return state
            
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            state["needs_search"] = False
            return state
    
    def _should_search(self, state: AssistantState) -> str:
        """Determine if knowledge search is needed"""
        return "search" if state["needs_search"] else "direct"
    
    def _search_knowledge(self, state: AssistantState) -> AssistantState:
        """Search knowledge base using RAG"""
        
        try:
            if not self.rag_connected:
                if not self._connect_rag():
                    state["rag_results"] = {
                        "response": "Xin lỗi, hệ thống tìm kiếm hiện không khả dụng.",
                        "sources": [],
                        "confidence": 0.0
                    }
                    return state
            
            # Get user query
            user_message = state["messages"][-1] if state["messages"] else None
            if not user_message:
                return state
            
            query = user_message.content
            
            # Search using RAG
            rag_results = self.rag_service.query(query, include_sources=True)
            state["rag_results"] = rag_results
            
            logger.info(f"RAG search completed with confidence: {rag_results.get('confidence', 0)}")
            return state
            
        except Exception as e:
            logger.error(f"Error in knowledge search: {e}")
            state["rag_results"] = {
                "response": f"Có lỗi xảy ra khi tìm kiếm: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
            return state
    
    def _generate_response(self, state: AssistantState) -> AssistantState:
        """Generate AI response using conversation context"""
        
        try:
            # Get conversation history
            history = self.memory_service.get_conversation_history(state["session_id"], limit=10)
            
            # Build context for response generation
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add conversation history
            messages.extend(history[-8:])  # Last 8 messages for context
            
            # Add current user message if not in history
            current_message = state["messages"][-1] if state["messages"] else None
            if current_message and current_message not in history:
                messages.append(current_message)
            
            # Add RAG results if available
            if state["rag_results"] and state["rag_results"].get("confidence", 0) > 0.3:
                rag_context = f"""
Thông tin từ cơ sở dữ liệu:
{state["rag_results"]['response']}

Nguồn tham khảo:
{chr(10).join([f"- {source['title']}: {source['section']}" for source in state["rag_results"].get('sources', [])[:3]])}
"""
                messages.append(SystemMessage(content=rag_context))
            
            # Generate response
            response = self.llm.invoke(messages)
            
            # Add response to state
            state["messages"].append(AIMessage(content=response.content))
            
            logger.info("Generated AI response successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_response = f"Xin lỗi, có lỗi xảy ra khi tạo phản hồi: {str(e)}"
            state["messages"].append(AIMessage(content=error_response))
            return state
    
    def _save_context(self, state: AssistantState) -> AssistantState:
        """Save conversation context to memory"""
        
        try:
            # Save all new messages to memory
            for message in state["messages"][-2:]:  # Save last 2 messages (user + AI)
                metadata = {
                    "rag_confidence": state["rag_results"].get("confidence", 0) if state["rag_results"] else 0,
                    "sources_count": len(state["rag_results"].get("sources", [])) if state["rag_results"] else 0,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.memory_service.save_message(
                    session_id=state["session_id"],
                    user_id=state["user_id"],
                    message=message,
                    metadata=metadata
                )
            
            logger.info(f"Saved conversation context for session {state['session_id']}")
            return state
            
        except Exception as e:
            logger.error(f"Error saving context: {e}")
            return state
    
    def _connect_rag(self) -> bool:
        """Connect to RAG service"""
        try:
            if self.rag_service.connect_milvus():
                self.rag_connected = True
                logger.info("Connected to RAG service")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect RAG service: {e}")
            return False
    
    async def chat(self, message: str, session_id: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Main chat interface
        
        Args:
            message: User message
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Chat response with metadata
        """
        
        try:
            # Create initial state
            state: AssistantState = {
                "messages": [HumanMessage(content=message)],
                "session_id": session_id,
                "user_id": user_id,
                "context": {},
                "rag_results": None,
                "needs_search": False,
                "conversation_summary": ""
            }
            
            # Run workflow
            final_state = self.workflow.invoke(state)
            
            # Extract response
            ai_response = final_state["messages"][-1] if final_state.get("messages") else None
            
            if not ai_response or not isinstance(ai_response, AIMessage):
                return {
                    "response": "Xin lỗi, có lỗi xảy ra trong quá trình xử lý.",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"error": "No AI response generated"}
                }
            
            # Prepare response
            response_data = {
                "response": ai_response.content,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "rag_used": final_state.get("needs_search", False),
                    "rag_confidence": final_state.get("rag_results", {}).get("confidence", 0) if final_state.get("rag_results") else 0,
                    "sources": final_state.get("rag_results", {}).get("sources", []) if final_state.get("rag_results") else [],
                    "conversation_length": len(final_state.get("messages", []))
                }
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return {
                "response": f"Xin lỗi, có lỗi xảy ra: {str(e)}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"error": str(e)}
            }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information and context"""
        
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
                "rag_connected": self.rag_connected
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {
                "session_id": session_id,
                "error": str(e)
            }
    
    def cleanup_old_sessions(self):
        """Clean up old conversation sessions"""
        try:
            self.memory_service.cleanup_old_sessions()
            logger.info("Cleaned up old conversation sessions")
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")

# Global instance
virtual_assistant = VirtualAssistantService()
