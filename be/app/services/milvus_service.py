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
    
    def get_all_chunks(self, limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
        """
        Get all chunks from Milvus collection with pagination
        
        Args:
            limit: Maximum number of chunks to return
            offset: Number of chunks to skip
            
        Returns:
            Dictionary with chunks data and metadata
        """
        try:
            if not self.collection:
                logger.error("❌ [MILVUS] Collection not initialized")
                return {"chunks": [], "total": 0, "error": "Collection not available"}
            
            logger.info(f"📋 [MILVUS] Fetching chunks with limit={limit}, offset={offset}")
            
            # Load collection to ensure data is available
            logger.info("🔄 [MILVUS] Loading collection...")
            self.collection.load()
            
            # Wait a moment for loading to complete
            import time
            time.sleep(1)
            
            # Get total count
            total_count = self.collection.num_entities
            logger.info(f"📊 [MILVUS] Total chunks in collection: {total_count}")
            
            # Query all chunks with pagination
            # Try different query expressions based on collection schema
            results = []
            
            try:
                # Method 1: Try with chunk_id field
                logger.debug("🔍 [MILVUS] Trying chunk_id >= 0 query...")
                results = self.collection.query(
                    expr="chunk_id >= 0",
                    output_fields=["file_name", "chunk_id", "content", "title", "section"],
                    limit=limit,
                    offset=offset
                )
                logger.debug(f"✅ [MILVUS] chunk_id query returned {len(results)} results")
                
            except Exception as e1:
                logger.warning(f"⚠️ [MILVUS] chunk_id query failed: {e1}")
                
                try:
                    # Method 2: Try with primary key
                    logger.debug("🔍 [MILVUS] Trying pk >= 0 query...")
                    results = self.collection.query(
                        expr="pk >= 0",
                        output_fields=["file_name", "chunk_id", "content", "title", "section"],
                        limit=limit,
                        offset=offset
                    )
                    logger.debug(f"✅ [MILVUS] pk query returned {len(results)} results")
                    
                except Exception as e2:
                    logger.warning(f"⚠️ [MILVUS] pk query failed: {e2}")
                    
                    try:
                        # Method 3: Try with file_name condition
                        logger.debug("🔍 [MILVUS] Trying file_name query...")
                        results = self.collection.query(
                            expr='file_name != ""',
                            output_fields=["file_name", "chunk_id", "content", "title", "section"],
                            limit=limit,
                            offset=offset
                        )
                        logger.debug(f"✅ [MILVUS] file_name query returned {len(results)} results")
                        
                    except Exception as e3:
                        logger.error(f"💥 [MILVUS] All query methods failed: {e3}")
                        # Log collection schema for debugging
                        try:
                            schema_fields = [field.name for field in self.collection.schema.fields]
                            logger.error(f"📋 [MILVUS] Collection fields: {schema_fields}")
                        except:
                            pass
            
            logger.info(f"✅ [MILVUS] Retrieved {len(results)} chunks")
            
            # Format results
            formatted_chunks = []
            for result in results:
                chunk_data = {
                    "id": result.get("chunk_id", 0),
                    "file_name": result.get("file_name", "Unknown"),
                    "title": result.get("title", "Untitled"),
                    "section": result.get("section", ""),
                    "content": result.get("content", ""),
                    "content_length": len(result.get("content", "")),
                    "content_preview": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", "")
                }
                formatted_chunks.append(chunk_data)
            
            # Sort by file_name and chunk_id for consistent ordering
            formatted_chunks.sort(key=lambda x: (x["file_name"], x["id"]))
            
            return {
                "chunks": formatted_chunks,
                "total": total_count,
                "retrieved": len(formatted_chunks),
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(formatted_chunks) < total_count
            }
            
        except Exception as e:
            logger.error(f"💥 [MILVUS] Failed to get all chunks: {e}", exc_info=True)
            return {
                "chunks": [],
                "total": 0,
                "error": str(e)
            }
    
    def get_chunks_by_file(self, file_name: str) -> List[Dict]:
        """
        Get all chunks for a specific file
        
        Args:
            file_name: Name of the file
            
        Returns:
            List of chunks for the specified file
        """
        try:
            if not self.collection:
                logger.error("❌ [MILVUS] Collection not initialized")
                return []
            
            logger.info(f"📋 [MILVUS] Fetching chunks for file: {file_name}")
            
            # Load collection if needed
            if not self.collection.is_loaded:
                self.collection.load()
            
            # Query chunks for specific file
            results = self.collection.query(
                expr=f'file_name == "{file_name}"',
                output_fields=["file_name", "chunk_id", "content", "title", "section"],
                limit=1000  # Reasonable limit for single file
            )
            
            logger.info(f"✅ [MILVUS] Retrieved {len(results)} chunks for {file_name}")
            
            # Format results
            formatted_chunks = []
            for result in results:
                chunk_data = {
                    "id": result.get("chunk_id", 0),
                    "file_name": result.get("file_name", "Unknown"),
                    "title": result.get("title", "Untitled"),
                    "section": result.get("section", ""),
                    "content": result.get("content", ""),
                    "content_length": len(result.get("content", "")),
                    "content_preview": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", "")
                }
                formatted_chunks.append(chunk_data)
            
            # Sort by chunk_id
            formatted_chunks.sort(key=lambda x: x["id"])
            
            return formatted_chunks
            
        except Exception as e:
            logger.error(f"💥 [MILVUS] Failed to get chunks for file {file_name}: {e}", exc_info=True)
            return []
    
    def delete_chunks_by_file(self, file_name: str) -> bool:
        """
        Delete all chunks for a specific file
        
        Args:
            file_name: Name of the file to delete chunks for
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if not self.collection:
                logger.error("❌ [MILVUS] Collection not initialized")
                return False
            
            logger.info(f"🗑️ [MILVUS] Deleting chunks for file: {file_name}")
            
            # Load collection if needed
            logger.info("🔄 [MILVUS] Loading collection for deletion...")
            self.collection.load()
            
            import time
            time.sleep(1)  # Wait for loading
            
            # Get collection schema to identify primary key field
            primary_key_field = None
            for field in self.collection.schema.fields:
                if field.is_primary:
                    primary_key_field = field.name
                    break
            
            if not primary_key_field:
                # Fallback to common primary key names
                primary_key_field = "pk"  # Default assumption
            
            logger.info(f"🔑 [MILVUS] Using primary key field: {primary_key_field}")
            
            # First, get count of chunks for this file
            delete_expr = f'file_name == "{file_name}"'
            logger.info(f"🔍 [MILVUS] Query expression: {delete_expr}")
            
            # Try different query methods to find chunks
            query_result = []
            
            try:
                # Method 1: Try with detected primary key field
                query_result = self.collection.query(
                    expr=delete_expr,
                    output_fields=[primary_key_field, "file_name"],
                    limit=10000
                )
                logger.info(f"📊 [MILVUS] Found {len(query_result)} chunks to delete")
                
            except Exception as e1:
                logger.warning(f"⚠️ [MILVUS] Primary key query failed: {e1}")
                
                # Method 2: Try with standard output fields
                try:
                    query_result = self.collection.query(
                        expr=delete_expr,
                        output_fields=["*"],  # Get all fields
                        limit=10000
                    )
                    logger.info(f"📊 [MILVUS] Found {len(query_result)} chunks with wildcard query")
                    
                except Exception as e2:
                    logger.error(f"💥 [MILVUS] All query methods failed: {e2}")
                    return False
            
            if not query_result:
                logger.warning(f"⚠️ [MILVUS] No chunks found for file: {file_name}")
                return True  # Not an error if no chunks exist
            
            # Debug: Show available fields
            if query_result:
                available_fields = list(query_result[0].keys())
                logger.info(f"🔍 [MILVUS] Available fields: {available_fields}")
            
            # Extract primary keys for deletion
            pks_to_delete = []
            
            # Try different primary key field names
            pk_field_candidates = [primary_key_field, "pk", "id", "_id", "auto_id"]
            
            for pk_field in pk_field_candidates:
                if query_result and pk_field in query_result[0]:
                    pks_to_delete = [item[pk_field] for item in query_result if pk_field in item]
                    logger.info(f"🔑 [MILVUS] Using pk field '{pk_field}', found {len(pks_to_delete)} keys")
                    break
            
            if not pks_to_delete:
                logger.error(f"❌ [MILVUS] No valid primary keys found. Available fields: {available_fields}")
                return False
            
            # Perform deletion in batches
            batch_size = 100
            total_deleted = 0
            
            for i in range(0, len(pks_to_delete), batch_size):
                batch_pks = pks_to_delete[i:i + batch_size]
                
                try:
                    # Delete batch using the identified primary key field
                    delete_expr_pk = f"{pk_field} in {batch_pks}"
                    delete_result = self.collection.delete(delete_expr_pk)
                    self.collection.flush()
                    
                    total_deleted += len(batch_pks)
                    logger.info(f"✅ [MILVUS] Deleted batch {i//batch_size + 1}: {len(batch_pks)} chunks")
                    
                except Exception as e:
                    logger.error(f"💥 [MILVUS] Failed to delete batch {i//batch_size + 1}: {e}")
                    # Continue with next batch
            
            logger.info(f"🎉 [MILVUS] Successfully deleted {total_deleted} chunks for file: {file_name}")
            return total_deleted > 0
            
        except Exception as e:
            logger.error(f"💥 [MILVUS] Failed to delete chunks for file {file_name}: {e}", exc_info=True)
            return False
    
    def get_collection_stats(self) -> int:
        """
        Get collection statistics
        
        Returns:
            Number of entities in collection
        """
        try:
            if not self.collection:
                return 0
            
            # Load collection if needed
            if not self.collection.is_loaded:
                self.collection.load()
            
            return self.collection.num_entities
        except Exception as e:
            logger.error(f"💥 [MILVUS] Failed to get collection stats: {e}")
            return 0
    
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
