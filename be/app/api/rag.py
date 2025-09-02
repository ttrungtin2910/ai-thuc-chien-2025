"""
RAG (Retrieval-Augmented Generation) API Routes
"""

from fastapi import APIRouter, HTTPException, Depends

from ..models.rag import RAGQuery, RAGResponse, MilvusStats
from ..core.security import verify_token
from ..services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["rag"])

# Initialize RAG service
rag_service = RAGService()


@router.post("/query", response_model=RAGResponse)
async def rag_query(
    query: RAGQuery,
    username: str = Depends(verify_token)
):
    """
    Query the RAG system with a question
    """
    try:
        # Ensure Milvus connection
        if not rag_service.milvus_connected:
            if not rag_service.connect_milvus():
                raise HTTPException(
                    status_code=503, 
                    detail="Vector database is not available. Please ensure Milvus is running."
                )
        
        # Process the query
        result = rag_service.query(
            question=query.question,
            include_sources=query.include_sources
        )
        
        # Convert to Pydantic model
        return RAGResponse(
            response=result["response"],
            confidence=result["confidence"],
            sources=[
                {
                    "title": source["title"],
                    "section": source["section"],
                    "file_name": source["file_name"],
                    "score": source["score"],
                    "content_preview": source["content_preview"]
                }
                for source in result["sources"]
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.get("/stats", response_model=MilvusStats)
async def get_rag_stats(username: str = Depends(verify_token)):
    """
    Get RAG system statistics
    """
    try:
        stats = rag_service.get_stats()
        return MilvusStats(
            milvus_connected=stats["milvus_connected"],
            openai_available=stats["openai_available"],
            collection_size=stats["collection_size"],
            embedding_model=stats["embedding_model"],
            chat_model=stats["chat_model"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/connect")
async def connect_milvus(username: str = Depends(verify_token)):
    """
    Manually connect to Milvus vector database
    """
    try:
        success = rag_service.connect_milvus()
        if success:
            return {"message": "Successfully connected to Milvus", "connected": True}
        else:
            raise HTTPException(status_code=503, detail="Failed to connect to Milvus")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")
