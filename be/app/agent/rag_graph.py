"""RAG Graph Builder for document-based question answering."""

import logging
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.constants import START, END

from .state import ChatState
from .nodes.transform_nodes import TransformQueryNode
from .nodes.retrieval_nodes import RetrieveNode, CachedDocumentsNode
from .nodes.generation_nodes import ContextGeneratorNode, PostProcessNode

logger = logging.getLogger(__name__)


class RAGGraphBuilder:
    """Builder for RAG (Retrieval-Augmented Generation) workflow graph."""
    
    def __init__(self):
        self.memory = MemorySaver()
        self.nodes = {
            "transform_query": TransformQueryNode(),
            "cached_documents": CachedDocumentsNode(),
            "retrieve": RetrieveNode(),
            "context_generator": ContextGeneratorNode(),
            "post_process": PostProcessNode(),
        }
    
    def build(self):
        """Build and compile the RAG graph."""
        graph = StateGraph(ChatState)
        
        # Add all nodes
        for name, node in self.nodes.items():
            graph.add_node(name, node)
        
        # Define the workflow
        graph.set_entry_point("transform_query")
        graph.add_edge("transform_query", "cached_documents")
        graph.add_edge("cached_documents", "retrieve")
        
        # Conditional routing after retrieval
        graph.add_conditional_edges(
            "retrieve",
            self.decide_to_generate,
            {
                "no_documents": "post_process",
                "generate": "context_generator",
            }
        )
        
        graph.add_edge("context_generator", "post_process")
        graph.add_edge("post_process", END)
        
        return graph.compile(checkpointer=self.memory)
    
    @staticmethod
    def decide_to_generate(state: ChatState) -> Literal["no_documents"] | Literal["generate"]:
        """Decide whether to generate response based on retrieved documents."""
        documents = state.documents
        
        if not documents:
            logger.info("No relevant documents found - returning no context response")
            return "no_documents"
        
        # Check document confidence/relevance
        high_confidence_docs = [
            doc for doc in documents 
            if doc.metadata.get('score', 0.0) >= 0.7
        ]
        
        if not high_confidence_docs:
            logger.info("No high-confidence documents - returning no context response")
            return "no_documents"
        
        logger.info(f"Found {len(high_confidence_docs)} high-confidence documents - proceeding to generation")
        return "generate"
