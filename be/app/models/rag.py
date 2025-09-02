"""
RAG Models

Pydantic models for Retrieval-Augmented Generation requests and responses.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RAGQuery(BaseModel):
    question: str
    include_sources: bool = True
    top_k: Optional[int] = 5


class RAGSource(BaseModel):
    title: str
    section: str
    file_name: str
    score: float
    content_preview: str


class RAGResponse(BaseModel):
    response: str
    confidence: float
    sources: List[RAGSource]


class MilvusStats(BaseModel):
    milvus_connected: bool
    openai_available: bool
    collection_size: int
    embedding_model: str
    chat_model: str
