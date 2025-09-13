#!/usr/bin/env python3
"""
Script to load all thutuccongdan documents into Milvus vector database
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to import modules
scripts_dir = os.path.dirname(os.path.abspath(__file__))
be_dir = os.path.dirname(scripts_dir)  # Go up one level to be/
sys.path.append(be_dir)

from app.services.milvus_service import MilvusService
from app.utils.document_processor import DocumentProcessor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to process and load documents"""
    
    print("=" * 60)
    print("LOADING THUTUCCONGDAN DOCUMENTS TO MILVUS")
    print("=" * 60)
    
    # Initialize services
    milvus_service = MilvusService(host="localhost", port="19530")
    document_processor = DocumentProcessor(data_dir="../data/thutuccongdan")
    
    try:
        # Step 1: Connect to Milvus
        print("\n🔗 Connecting to Milvus...")
        if not milvus_service.connect():
            print("❌ Failed to connect to Milvus. Make sure Milvus is running.")
            print("   Run: docker-compose -f docker-compose-milvus.yml up -d")
            return False
        print("✅ Connected to Milvus successfully")
        
        # Step 2: Create collection with OpenAI embedding dimension (3072)
        print("\n📦 Creating collection...")
        if not milvus_service.create_collection(dimension=3072):
            print("❌ Failed to create collection")
            return False
        print("✅ Collection created successfully (dimension: 3072 for text-embedding-3-large)")
        
        # Step 3: Load collection to memory
        print("\n💾 Loading collection to memory...")
        if not milvus_service.load_collection():
            print("❌ Failed to load collection")
            return False
        print("✅ Collection loaded to memory")
        
        # Step 4: Read and process documents
        print("\n📖 Reading markdown documents...")
        documents = document_processor.read_markdown_files()
        if not documents:
            print("❌ No documents found")
            return False
        print(f"✅ Read {len(documents)} documents")
        
        # Step 5: Create chunks
        print("\n✂️ Creating document chunks...")
        chunks = document_processor.chunk_documents(documents)
        if not chunks:
            print("❌ No chunks created")
            return False
        print(f"✅ Created {len(chunks)} chunks")
        
        # Step 6: Insert documents in batches
        print("\n⬆️ Inserting documents to Milvus...")
        batch_size = 50  # Process in batches to avoid memory issues
        total_chunks = len(chunks)
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size
            
            print(f"   Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
            
            if not milvus_service.insert_documents(batch):
                print(f"❌ Failed to insert batch {batch_num}")
                return False
            
            # Small delay between batches
            time.sleep(0.5)
        
        print("✅ All documents inserted successfully")
        
        # Step 7: Get collection statistics
        print("\n📊 Collection statistics:")
        stats = milvus_service.get_collection_stats()
        print(f"   Total entities: {stats}")
        
        # Step 8: Test search functionality
        print("\n🔍 Testing search functionality...")
        test_query = "đăng ký thường trú"
        results = milvus_service.search_similar(test_query, top_k=3)
        
        if results:
            print(f"✅ Search test successful. Found {len(results)} results for '{test_query}':")
            for i, result in enumerate(results[:2], 1):
                print(f"   {i}. {result['title']} (Score: {result['score']:.4f})")
                print(f"      Section: {result['section']}")
                print(f"      Content preview: {result['content'][:100]}...")
                print()
        else:
            print("⚠️ Search test returned no results")
        
        print("\n🎉 SUCCESS! All documents have been loaded to Milvus")
        print("\nNext steps:")
        print("- Access Attu web interface at: http://localhost:3001")
        print("- Use the search functionality in your application")
        print("- The collection name is: 'document_embeddings'")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        print(f"❌ Error: {e}")
        return False
        
    finally:
        # Disconnect from Milvus
        milvus_service.disconnect()

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if data directory exists
    data_dir = Path("../data/thutuccongdan")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    # Check if markdown files exist
    md_files = list(data_dir.glob("*.md"))
    if not md_files:
        print(f"❌ No markdown files found in {data_dir}")
        return False
    
    print(f"✅ Found {len(md_files)} markdown files")
    
    # Check if required packages are installed
    try:
        import pymilvus
        print("✅ Required packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

if __name__ == "__main__":
    print("Thutuccongdan Document Loader for Milvus")
    print("========================================")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Run main process
    success = main()
    
    if success:
        print("\n✅ Process completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Process failed!")
        sys.exit(1)
