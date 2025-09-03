"""Document retrieval nodes."""

import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

from .base_node import BaseNode
from ..state import ChatState
from ..configuration import Configuration
from ...services.milvus_service import MilvusService
from ..utils import calculate_confidence

logger = logging.getLogger(__name__)


class RetrieveNode(BaseNode):
    """Node to retrieve relevant documents from vector database."""
    
    def __init__(self):
        self.milvus_service = MilvusService()
        self.connected = False
    
    async def connect_if_needed(self):
        """Connect to Milvus if not already connected."""
        if not self.connected:
            try:
                if self.milvus_service.connect():
                    from pymilvus import Collection
                    self.milvus_service.collection = Collection("document_embeddings")
                    if self.milvus_service.load_collection():
                        self.connected = True
                        logger.info("Connected to Milvus successfully")
                        return True
                logger.error("Failed to connect to Milvus")
                return False
            except Exception as e:
                logger.error(f"Error connecting to Milvus: {e}")
                return False
        return True
    
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Retrieve relevant documents for the query."""
        try:
            # Connect to Milvus if needed
            if not await self.connect_if_needed():
                logger.error("Cannot retrieve documents - Milvus not connected")
                return {"documents": [], "confidence": 0.0}
            
            query = state.better_query or (state.messages[-1].content if state.messages else "")
            if not query.strip():
                logger.warning("Empty query for retrieval")
                return {"documents": [], "confidence": 0.0}
            
            # Get configuration
            configuration = Configuration.from_runnable_config(config)
            top_k = configuration.max_search_results
            
            # Perform search
            search_results = self.milvus_service.search_similar(query, top_k=top_k)
            
            # Convert to Langchain Documents
            documents = []
            for result in search_results:
                doc = Document(
                    page_content=result.get('content', ''),
                    metadata={
                        'title': result.get('title', 'Unknown'),
                        'section': result.get('section', 'Unknown'),
                        'file_name': result.get('file_name', 'Unknown'),
                        'score': result.get('score', 0.0)
                    }
                )
                documents.append(doc)
            
            # Calculate confidence
            confidence = calculate_confidence(documents)
            
            logger.info(f"Retrieved {len(documents)} documents with confidence {confidence:.3f}")
            
            # Log document details
            for idx, doc in enumerate(documents[:3]):  # Log first 3
                logger.info(f"Doc {idx+1}: {doc.metadata.get('title')} (score: {doc.metadata.get('score', 0):.3f})")
            
            return {
                "documents": documents,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error in document retrieval: {e}")
            return {"documents": [], "confidence": 0.0}


class CachedDocumentsNode(BaseNode):
    """Node to check for cached documents (placeholder for future enhancement)."""
    
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Check for cached documents - currently a pass-through."""
        logger.info("Cached documents check (pass-through)")
        return {"retrieved_documents": []}  # Could implement caching logic here
