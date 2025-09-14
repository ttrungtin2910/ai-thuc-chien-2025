import os
import json
from typing import List, Dict, Any
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from .openai_service import openai_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MilvusService:
    def __init__(self, host: str = "localhost", port: str = "19530"):
        """
        Initialize Milvus service
        
        Args:
            host: Milvus server host
            port: Milvus server port
        """
        self.host = host
        self.port = port
        self.collection_name = "document_embeddings"
        # Use OpenAI embeddings instead of sentence transformers
        self.collection = None
        
    def connect(self):
        """Connect to Milvus server"""
        try:
            connections.connect("default", host=self.host, port=self.port)
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            return False
    
    def create_collection(self, dimension: int = None):
        """
        Create collection for storing document embeddings
        
        Args:
            dimension: Vector dimension (auto-detected from OpenAI service, default 3072 for text-embedding-3-large)
        """
        if dimension is None:
            # Auto-detect dimension from OpenAI service
            dimension = openai_service.get_embedding_dimension()
            logger.info(f"Using embedding dimension: {dimension} for model: {openai_service.embedding_model}")
        try:
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                self.collection = Collection(self.collection_name)
                return True
            
            # Define fields
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="chunk_id", dtype=DataType.INT64),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8192),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="section", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
            ]
            
            # Create schema
            schema = CollectionSchema(fields, "Document embeddings for RAG")
            
            # Create collection
            self.collection = Collection(self.collection_name, schema)
            logger.info(f"Created collection '{self.collection_name}'")
            
            # Create index for vector field
            index_params = {
                "metric_type": "IP",  # Inner Product
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            self.collection.create_index("embedding", index_params)
            logger.info("Created index for embedding field")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def load_collection(self):
        """Load collection to memory"""
        try:
            if self.collection:
                self.collection.load()
                logger.info(f"Loaded collection '{self.collection_name}' to memory")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load collection: {e}")
            return False
    
    def insert_documents(self, documents: List[Dict[str, Any]]):
        """
        Insert documents into Milvus
        
        Args:
            documents: List of document dictionaries with keys:
                      - file_name, chunk_id, content, title, section
        """
        logger.info(f"🚀 [MILVUS] Starting to insert {len(documents)} documents")
        
        try:
            if not self.collection:
                logger.error("❌ [MILVUS] Collection not initialized")
                return False
            
            logger.info(f"✅ [MILVUS] Collection available: {self.collection_name}")
            
            # Prepare texts for batch embedding
            texts = [doc["content"] for doc in documents]
            logger.info(f"📝 [MILVUS] Preparing {len(texts)} texts for embedding")
            
            # Generate embeddings using OpenAI
            logger.info(f"🤖 [MILVUS] Generating embeddings using OpenAI...")
            embeddings = openai_service.get_embeddings(texts)
            
            if not embeddings:
                logger.error("❌ [MILVUS] Failed to generate embeddings")
                return False
            
            logger.info(f"✅ [MILVUS] Generated {len(embeddings)} embeddings")
            logger.info(f"📊 [MILVUS] Embedding dimension: {len(embeddings[0]) if embeddings else 'Unknown'}")
            
            # Prepare data for insertion - ensure correct data types
            file_names = []
            chunk_ids = []
            contents = []
            titles = []
            sections = []
            embedding_vectors = []
            
            logger.info(f"🔧 [MILVUS] Preparing data for insertion...")
            for i, doc in enumerate(documents):
                file_names.append(str(doc["file_name"]))
                chunk_ids.append(int(doc["chunk_id"]))
                contents.append(str(doc["content"]))
                titles.append(str(doc["title"]))
                sections.append(str(doc["section"]))
                embedding_vectors.append(embeddings[i])
                logger.debug(f"📄 [MILVUS] Doc {i}: {doc['file_name']}, chunk {doc['chunk_id']}, content length: {len(doc['content'])}")
            
            # Insert data with correct structure
            data = [file_names, chunk_ids, contents, titles, sections, embedding_vectors]
            logger.info(f"💾 [MILVUS] Inserting data into collection...")
            
            # Insert data
            insert_result = self.collection.insert(data)
            logger.info(f"✅ [MILVUS] Data inserted, flushing collection...")
            self.collection.flush()
            
            logger.info(f"🎉 [MILVUS] Successfully inserted {len(documents)} documents")
            logger.info(f"🔑 [MILVUS] Primary keys sample: {insert_result.primary_keys[:5]}...")
            
            # Get updated stats
            stats = self.get_collection_stats()
            logger.info(f"📊 [MILVUS] Collection stats after insert: {stats} total entities")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 [MILVUS] Failed to insert documents: {e}", exc_info=True)
            return False
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of similar documents with metadata
        """
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return []
            
            # Generate query embedding using OpenAI
            query_embedding = openai_service.get_embedding(query)
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search parameters
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["file_name", "chunk_id", "content", "title", "section"]
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    formatted_results.append({
                        "id": hit.id,
                        "score": hit.score,
                        "file_name": hit.entity.get("file_name"),
                        "chunk_id": hit.entity.get("chunk_id"),
                        "content": hit.entity.get("content"),
                        "title": hit.entity.get("title"),
                        "section": hit.entity.get("section")
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []
    
    def get_collection_stats(self):
        """Get collection statistics"""
        try:
            if self.collection:
                stats = self.collection.num_entities
                logger.info(f"Collection '{self.collection_name}' has {stats} entities")
                return stats
            return 0
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return 0
    
    def disconnect(self):
        """Disconnect from Milvus"""
        try:
            connections.disconnect("default")
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
