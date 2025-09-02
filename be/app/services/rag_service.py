"""
RAG (Retrieval-Augmented Generation) Service
Combines Milvus vector search with Azure OpenAI for intelligent Q&A
"""

import os
import logging
from typing import List, Dict, Any, Optional
from .milvus_service import MilvusService
from .openai_service import openai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        """Initialize RAG service with Milvus and Azure OpenAI"""
        
        # Initialize Milvus
        self.milvus = MilvusService()
        self.milvus_connected = False
        
        # Use OpenAI service for chat completions
        
        # RAG parameters
        self.top_k = 5  # Number of documents to retrieve
        self.max_context_length = 4000  # Maximum context characters
        

    
    def connect_milvus(self) -> bool:
        """Connect to Milvus vector database"""
        try:
            if self.milvus.connect():
                # Load collection
                from pymilvus import Collection
                self.milvus.collection = Collection("document_embeddings")
                if self.milvus.load_collection():
                    self.milvus_connected = True
                    logger.info("Connected to Milvus successfully")
                    return True
            
            logger.error("Failed to connect to Milvus")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to Milvus: {e}")
            return False
    
    def retrieve_documents(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from Milvus
        
        Args:
            query: User question/query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        if not self.milvus_connected:
            logger.error("Milvus not connected")
            return []
        
        k = top_k or self.top_k
        
        try:
            results = self.milvus.search_similar(query, top_k=k)
            logger.info(f"Retrieved {len(results)} documents for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "Không tìm thấy thông tin liên quan."
        
        context_parts = []
        current_length = 0
        
        for doc in documents:
            # Format document info
            doc_info = f"""
Tài liệu: {doc['title']}
Phần: {doc['section']}
Nội dung: {doc['content']}
---
"""
            
            # Check if adding this document exceeds max length
            if current_length + len(doc_info) > self.max_context_length:
                break
            
            context_parts.append(doc_info)
            current_length += len(doc_info)
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> str:
        """
        Generate response using OpenAI with context
        
        Args:
            query: User question
            context: Retrieved context from documents
            
        Returns:
            Generated response
        """
        if not openai_service.enabled:
            return "Xin lỗi, dịch vụ AI hiện không khả dụng."
        
        try:
            # Create system prompt
            system_prompt = """Bạn là một trợ lý AI chuyên về thủ tục hành chính công dân Việt Nam. 
Hãy trả lời câu hỏi dựa trên thông tin được cung cấp một cách chính xác, chi tiết và hữu ích.

Quy tắc:
1. Chỉ sử dụng thông tin từ tài liệu được cung cấp
2. Nếu không có thông tin liên quan, hãy nói rằng bạn không có đủ thông tin
3. Trả lời bằng tiếng Việt
4. Cấu trúc câu trả lời rõ ràng, dễ hiểu
5. Nếu có quy trình, hãy liệt kê từng bước cụ thể"""
            
            # Create user prompt
            user_prompt = f"""
Thông tin tham khảo:
{context}

Câu hỏi: {query}

Hãy trả lời câu hỏi dựa trên thông tin trên."""
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call OpenAI
            response = openai_service.chat_completion(messages)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Xin lỗi, đã có lỗi xảy ra khi tạo câu trả lời: {str(e)}"
    
    def query(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """
        Main RAG query function
        
        Args:
            question: User question
            include_sources: Whether to include source documents
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Step 1: Retrieve relevant documents
            documents = self.retrieve_documents(question)
            
            if not documents:
                return {
                    "response": "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Step 2: Format context
            context = self.format_context(documents)
            
            # Step 3: Generate response
            response = self.generate_response(question, context)
            
            # Step 4: Prepare result
            result = {
                "response": response,
                "confidence": documents[0]["score"] if documents else 0.0
            }
            
            if include_sources:
                result["sources"] = [
                    {
                        "title": doc["title"],
                        "section": doc["section"],
                        "file_name": doc["file_name"],
                        "score": doc["score"],
                        "content_preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                    }
                    for doc in documents[:3]  # Top 3 sources
                ]
            else:
                result["sources"] = []
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "response": f"Xin lỗi, đã có lỗi xảy ra: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        stats = {
            "milvus_connected": self.milvus_connected,
            "openai_available": openai_service.enabled,
            "collection_size": 0,
            "embedding_model": openai_service.embedding_model,
            "chat_model": openai_service.chat_model
        }
        
        if self.milvus_connected:
            stats["collection_size"] = self.milvus.get_collection_stats()
        
        return stats

# Example usage
if __name__ == "__main__":
    # Initialize RAG service
    rag = RAGService()
    
    # Connect to Milvus
    if not rag.connect_milvus():
        print("Failed to connect to Milvus")
        exit(1)
    
    # Test queries
    test_queries = [
        "Thủ tục đăng ký thường trú như thế nào?",
        "Cần những giấy tờ gì để làm căn cước công dân?",
        "Quy trình xin cấp hộ chiếu mới?",
        "Thời gian xử lý hồ sơ là bao lâu?"
    ]
    
    print("=== RAG Service Test ===")
    for query in test_queries:
        print(f"\n🔍 Câu hỏi: {query}")
        result = rag.query(query)
        print(f"📝 Trả lời: {result['response']}")
        print(f"🎯 Độ tin cậy: {result['confidence']:.4f}")
        
        if result['sources']:
            print("📚 Nguồn tham khảo:")
            for i, source in enumerate(result['sources'], 1):
                print(f"   {i}. {source['title']} - {source['section']} (Score: {source['score']:.4f})")
        
        print("-" * 60)
