"""Main Graph Builder for the complete agent workflow."""

import logging
from typing import Literal, cast
from langgraph.checkpoint.memory import MemorySaver  
from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langchain_core.messages import AIMessage

from .state import State, InputState
from .configuration import Configuration
from .rag_graph import RAGGraphBuilder
from .nodes.routing_nodes import AnalyzeQueryNode
from .nodes.generation_nodes import GenericResponseNode

logger = logging.getLogger(__name__)


class MainGraphBuilder:
    """Builder for the main agent workflow graph."""
    
    def __init__(self):
        self.memory = MemorySaver()
        self.rag_graph = RAGGraphBuilder().build()
        
        # Initialize nodes
        self.analyze_node = AnalyzeQueryNode()
        self.generic_node = GenericResponseNode()
    
    def compile_graph(self, checkpointer=None):
        """Compile the complete agent graph."""
        graph_builder = self.create_graph()
        if checkpointer is None:
            checkpointer = self.memory
        return graph_builder.compile(checkpointer=checkpointer)
    
    def create_graph(self):
        """Create the main agent graph structure."""
        builder = StateGraph(State, input=InputState, config_schema=Configuration)
        
        # Add nodes
        builder.add_node("analyze_query", self.analyze_query)
        builder.add_node("rag_response", self.rag_response)
        builder.add_node("generic_response", self.generic_response)
        
        # Define workflow
        builder.add_edge(START, "analyze_query")
        
        # Conditional routing based on query analysis
        builder.add_conditional_edges(
            "analyze_query",
            self.route_query,
            {
                "rag": "rag_response",
                "generic": "generic_response"
            }
        )
        
        builder.add_edge("rag_response", END)
        builder.add_edge("generic_response", END)
        
        return builder
    
    async def analyze_query(self, state: State, config):
        """Analyze incoming query and prepare for routing."""
        try:
            # Create proper ChatState instance
            from .state import ChatState
            
            chat_state = ChatState(
                messages=state.messages,
                session_id=state.session_id,
                user_id=state.user_id,
                memories=state.memories
            )
            
            # Use the analysis node
            result = await self.analyze_node(chat_state, config)
            
            logger.info(f"Analysis node returned: {result}")
            
            # Update state with analysis results
            updates = {
                "needs_search": result.get("needs_search", False),
                "route_destination": result.get("route_destination", "casual"),
                "language": result.get("language", "vi")
            }
            
            logger.info(f"State updates: {updates}")
            return updates
            
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            return {
                "needs_search": False,
                "route_destination": "casual", 
                "language": "vi"
            }
    
    def route_query(self, state: State) -> Literal["rag"] | Literal["generic"]:
        """Route query based on analysis results."""
        # Get the analysis results from the state update
        needs_search = getattr(state, 'needs_search', False)
        route_destination = getattr(state, 'route_destination', 'casual')
        
        logger.info(f"Route decision: needs_search={needs_search}, route_destination={route_destination}")
        
        if needs_search and route_destination == "other":
            logger.info("Routing to RAG workflow")
            return "rag"
        else:
            logger.info("Routing to generic response")
            return "generic"
    
    async def rag_response(self, state: State, config):
        """Handle RAG-based responses using existing RAG service."""
        try:
            # Import RAG service
            from ..services.rag_service import RAGService
            
            # Get user query
            user_message = state.messages[-1] if state.messages else None
            if not user_message:
                raise ValueError("No user message found")
            
            query = user_message.content
            
            # Initialize RAG service
            rag_service = RAGService()
            
            # Connect to Milvus if needed
            if not rag_service.connect_milvus():
                logger.warning("Could not connect to Milvus, providing fallback response")
                message = AIMessage(
                    content="Xin lỗi, hệ thống tìm kiếm hiện không khả dụng. Vui lòng thử lại sau.",
                    additional_kwargs={
                        "rag_used": False,
                        "error": "Milvus connection failed"
                    }
                )
                return {"messages": [message]}
            
            # Perform RAG query
            rag_result = rag_service.query(query, include_sources=True)
            
            # Extract response and metadata
            response_content = rag_result.get("response", "Xin lỗi, không tìm thấy thông tin liên quan.")
            sources = rag_result.get("sources", [])
            confidence = rag_result.get("confidence", 0.0)
            
            # Format source information
            source_info = ""
            if sources:
                source_info = "\n\nNguồn tham khảo:\n"
                for i, source in enumerate(sources[:3], 1):
                    source_info += f"{i}. {source['title']} - {source['section']}\n"
            
            # Create final response
            if source_info and confidence > 0.3:
                final_content = f"{response_content}{source_info}"
            else:
                final_content = response_content
            
            # Create AI message
            message = AIMessage(
                content=final_content,
                additional_kwargs={
                    "extracted_entities": [str(i) for i in range(1, len(sources[:3]) + 1)],
                    "source_info": source_info.strip(),
                    "confidence": confidence,
                    "rag_used": True,
                    "sources_count": len(sources)
                }
            )
            
            logger.info(f"RAG response generated successfully with confidence {confidence:.3f}")
            return {"messages": [message]}
            
        except Exception as e:
            logger.error(f"Error in RAG response: {e}")
            error_message = AIMessage(
                content="Xin lỗi, có lỗi xảy ra khi tìm kiếm thông tin.",
                additional_kwargs={"error": str(e), "rag_used": False}
            )
            return {"messages": [error_message]}
    
    async def generic_response(self, state: State, config):
        """Handle generic conversational responses."""
        try:
            # Convert to ChatState for generic processing
            chat_state = type('ChatState', (), {
                "messages": state.messages,
                "session_id": getattr(state, 'session_id', ''),
                "user_id": getattr(state, 'user_id', 'anonymous'),
                "memories": state.memories,
                "language": getattr(state, 'language', 'vi')
            })()
            
            # Generate generic response
            result = await self.generic_node(chat_state, config)
            
            # Create AI message
            message = AIMessage(
                content=result.get("generation", "Xin chào! Tôi có thể giúp gì cho bạn?"),
                additional_kwargs={
                    "rag_used": False,
                    "response_type": "generic"
                }
            )
            
            logger.info("Generic response generated successfully")
            return {"messages": [message]}
            
        except Exception as e:
            logger.error(f"Error in generic response: {e}")
            error_message = AIMessage(
                content="Xin chào! Tôi có thể giúp gì cho bạn?",
                additional_kwargs={"error": str(e), "rag_used": False}
            )
            return {"messages": [error_message]}
