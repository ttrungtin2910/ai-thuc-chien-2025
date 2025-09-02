#!/usr/bin/env python3
"""
Test script for RAG system with Milvus and Azure OpenAI
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
scripts_dir = os.path.dirname(os.path.abspath(__file__))
be_dir = os.path.dirname(scripts_dir)  # Go up one level to be/
sys.path.append(be_dir)

from app.services.rag_service import RAGService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment():
    """Test if environment is properly configured"""
    print("🔍 Testing environment configuration...")
    
    issues = []
    
    # Check Azure OpenAI environment variables
    required_env_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "OPENAI_API_VERSION",
        "OPENAI_MODEL_NAME"
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            issues.append(f"Missing environment variable: {var}")
    
    # Check if data directory exists
    data_dir = Path("../data/thutuccongdan")
    if not data_dir.exists():
        issues.append(f"Data directory not found: {data_dir}")
    
    if issues:
        print("❌ Environment issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ Environment configuration OK")
    return True

def test_milvus_connection():
    """Test Milvus connection and data"""
    print("\n📦 Testing Milvus connection...")
    
    try:
        rag = RAGService()
        
        # Connect to Milvus
        if not rag.connect_milvus():
            print("❌ Failed to connect to Milvus")
            print("   Make sure Milvus is running: docker-compose -f docker-compose-milvus.yml up -d")
            return False, None
        
        # Check collection stats
        stats = rag.get_stats()
        collection_size = stats.get("collection_size", 0)
        
        if collection_size == 0:
            print("❌ No documents found in Milvus collection")
            print("   Run the document loader: python load_documents_to_milvus.py")
            return False, rag
        
        print(f"✅ Connected to Milvus successfully")
        print(f"   Collection size: {collection_size} documents")
        return True, rag
        
    except Exception as e:
        print(f"❌ Error testing Milvus: {e}")
        return False, None

def test_vector_search(rag_service):
    """Test vector search functionality"""
    print("\n🔍 Testing vector search...")
    
    test_query = "đăng ký thường trú"
    
    try:
        results = rag_service.retrieve_documents(test_query, top_k=3)
        
        if not results:
            print("❌ No search results returned")
            return False
        
        print(f"✅ Search successful - found {len(results)} results")
        print("   Top result:")
        top_result = results[0]
        print(f"   - Title: {top_result['title']}")
        print(f"   - Section: {top_result['section']}")
        print(f"   - Score: {top_result['score']:.4f}")
        print(f"   - Content preview: {top_result['content'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in vector search: {e}")
        return False

def test_rag_pipeline(rag_service):
    """Test full RAG pipeline"""
    print("\n🤖 Testing full RAG pipeline...")
    
    test_questions = [
        "Thủ tục đăng ký thường trú như thế nào?",
        "Cần những giấy tờ gì để làm căn cước công dân?",
        "Thời gian xử lý hồ sơ là bao lâu?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        
        try:
            result = rag_service.query(question, include_sources=True)
            
            if not result["response"]:
                print("❌ Empty response")
                continue
            
            print(f"✅ Response generated successfully")
            print(f"   Confidence: {result['confidence']:.4f}")
            print(f"   Sources: {len(result['sources'])} documents")
            print(f"   Response preview: {result['response'][:150]}...")
            
            # Show first source
            if result['sources']:
                source = result['sources'][0]
                print(f"   Top source: {source['title']} - {source['section']}")
            
        except Exception as e:
            print(f"❌ Error in RAG query: {e}")
            return False
    
    return True

def interactive_test(rag_service):
    """Interactive testing mode"""
    print("\n💬 Interactive testing mode")
    print("Enter your questions (type 'quit' to exit):")
    print("-" * 50)
    
    while True:
        try:
            question = input("\n🔍 Your question: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            print("🤔 Thinking...")
            result = rag_service.query(question, include_sources=True)
            
            print(f"\n🤖 Answer:")
            print(result['response'])
            
            if result['sources']:
                print(f"\n📚 Sources (confidence: {result['confidence']:.4f}):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"   {i}. {source['title']} - {source['section']}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("RAG SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Environment
    if not test_environment():
        print("\n❌ Environment test failed")
        return False
    
    # Test 2: Milvus connection
    milvus_ok, rag_service = test_milvus_connection()
    if not milvus_ok:
        print("\n❌ Milvus test failed")
        return False
    
    # Test 3: Vector search
    if not test_vector_search(rag_service):
        print("\n❌ Vector search test failed")
        return False
    
    # Test 4: RAG pipeline
    if not test_rag_pipeline(rag_service):
        print("\n❌ RAG pipeline test failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    
    # Optional interactive mode
    choice = input("\nDo you want to try interactive mode? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        interactive_test(rag_service)
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ RAG system is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ RAG system has issues. Please check the logs above.")
        sys.exit(1)
