"""
MongoDB database module for document management
"""
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError
from ..core.config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """MongoDB database manager for document operations"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.documents_collection: Optional[Collection] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            # Connect to MongoDB
            self.client = MongoClient(
                Config.MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[Config.MONGODB_DATABASE]
            self.documents_collection = self.db.documents
            
            # Create indexes for better performance
            self.documents_collection.create_index("id", unique=True)
            self.documents_collection.create_index("filename")
            self.documents_collection.create_index("file_type")
            self.documents_collection.create_index("upload_date")
            
            logger.info(f"✅ Connected to MongoDB: {Config.MONGODB_URL}/{Config.MONGODB_DATABASE}")
            
        except ConnectionFailure as e:
            logger.warning(f"⚠️ Cannot connect to MongoDB: {e}")
            logger.warning("🔄 Falling back to in-memory storage")
            self.client = None
            self.db = None
            self.documents_collection = None
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            self.client = None
            self.db = None
            self.documents_collection = None
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        try:
            if self.client is None:
                return False
            self.client.admin.command('ping')
            return True
        except:
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔴 MongoDB connection closed")

# Global database manager instance
db_manager = DatabaseManager()

# Fallback in-memory storage for when MongoDB is not available
_fallback_documents: List[Dict] = []

def add_document(filename: str, file_type: str, size: int, public_url: str = None, stored_filename: str = None) -> Dict:
    """
    Add document to database
    
    Args:
        filename: Original filename
        file_type: File extension (e.g., .pdf, .docx)
        size: File size in bytes
        public_url: Public URL for accessing the file
        stored_filename: Stored filename for deletion reference
        
    Returns:
        Document dictionary with id and metadata
    """
    document = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "file_type": file_type,
        "upload_date": datetime.now().isoformat(),
        "size": size,
        "public_url": public_url,
        "status": "completed",
        "stored_filename": stored_filename or filename
    }
    
    try:
        if db_manager.is_connected():
            # Use MongoDB
            result = db_manager.documents_collection.insert_one(document)
            if result.inserted_id:
                logger.info(f"📝 Document added to MongoDB: {filename} (ID: {document['id']})")
                return document
            else:
                raise Exception("Failed to insert document")
                
    except Exception as e:
        logger.warning(f"⚠️ MongoDB insert failed: {e}, using fallback storage")
    
    # Fallback to in-memory storage
    global _fallback_documents
    _fallback_documents.append(document)
    logger.info(f"📝 Document added to fallback storage: {filename} (ID: {document['id']})")
    return document

def get_documents() -> List[Dict]:
    """
    Get all documents from database
    
    Returns:
        List of document dictionaries
    """
    try:
        if db_manager.is_connected():
            # Use MongoDB
            documents = list(db_manager.documents_collection.find({}, {"_id": 0}))
            logger.debug(f"📖 Retrieved {len(documents)} documents from MongoDB")
            return documents
            
    except Exception as e:
        logger.warning(f"⚠️ MongoDB query failed: {e}, using fallback storage")
    
    # Fallback to in-memory storage
    global _fallback_documents
    logger.debug(f"📖 Retrieved {len(_fallback_documents)} documents from fallback storage")
    return _fallback_documents.copy()

def get_document_by_id(document_id: str) -> Optional[Dict]:
    """
    Get document by ID
    
    Args:
        document_id: Document ID
        
    Returns:
        Document dictionary or None if not found
    """
    try:
        if db_manager.is_connected():
            # Use MongoDB
            document = db_manager.documents_collection.find_one(
                {"id": document_id}, 
                {"_id": 0}
            )
            if document:
                logger.debug(f"🔍 Found document in MongoDB: {document_id}")
                return document
            else:
                logger.debug(f"🔍 Document not found in MongoDB: {document_id}")
                return None
                
    except Exception as e:
        logger.warning(f"⚠️ MongoDB query failed: {e}, using fallback storage")
    
    # Fallback to in-memory storage
    global _fallback_documents
    for doc in _fallback_documents:
        if doc["id"] == document_id:
            logger.debug(f"🔍 Found document in fallback storage: {document_id}")
            return doc
    
    logger.debug(f"🔍 Document not found in fallback storage: {document_id}")
    return None

def delete_document(document_id: str) -> bool:
    """
    Delete document from database
    
    Args:
        document_id: Document ID
        
    Returns:
        True if deleted, False if not found
    """
    try:
        if db_manager.is_connected():
            # Use MongoDB
            result = db_manager.documents_collection.delete_one({"id": document_id})
            if result.deleted_count > 0:
                logger.info(f"🗑️ Document deleted from MongoDB: {document_id}")
                return True
            else:
                logger.debug(f"🔍 Document not found for deletion in MongoDB: {document_id}")
                return False
                
    except Exception as e:
        logger.warning(f"⚠️ MongoDB delete failed: {e}, using fallback storage")
    
    # Fallback to in-memory storage
    global _fallback_documents
    for i, doc in enumerate(_fallback_documents):
        if doc["id"] == document_id:
            deleted_doc = _fallback_documents.pop(i)
            logger.info(f"🗑️ Document deleted from fallback storage: {deleted_doc['filename']} (ID: {document_id})")
            return True
    
    logger.debug(f"🔍 Document not found for deletion in fallback storage: {document_id}")
    return False

def get_documents_count() -> int:
    """
    Get total number of documents
    
    Returns:
        Number of documents
    """
    try:
        if db_manager.is_connected():
            # Use MongoDB
            count = db_manager.documents_collection.count_documents({})
            logger.debug(f"📊 Document count from MongoDB: {count}")
            return count
            
    except Exception as e:
        logger.warning(f"⚠️ MongoDB count failed: {e}, using fallback storage")
    
    # Fallback to in-memory storage
    global _fallback_documents
    count = len(_fallback_documents)
    logger.debug(f"📊 Document count from fallback storage: {count}")
    return count

def get_documents_by_type(file_type: str) -> List[Dict]:
    """
    Get documents by file type
    
    Args:
        file_type: File extension (e.g., .pdf, .docx)
        
    Returns:
        List of matching documents
    """
    try:
        if db_manager.is_connected():
            # Use MongoDB
            documents = list(db_manager.documents_collection.find(
                {"file_type": file_type}, 
                {"_id": 0}
            ))
            logger.debug(f"📊 Found {len(documents)} documents of type {file_type} in MongoDB")
            return documents
            
    except Exception as e:
        logger.warning(f"⚠️ MongoDB query failed: {e}, using fallback storage")
    
    # Fallback to in-memory storage
    global _fallback_documents
    documents = [doc for doc in _fallback_documents if doc["file_type"] == file_type]
    logger.debug(f"📊 Found {len(documents)} documents of type {file_type} in fallback storage")
    return documents

def clear_all_documents() -> bool:
    """
    Clear all documents (for testing purposes)
    
    Returns:
        True if successful
    """
    try:
        if db_manager.is_connected():
            # Use MongoDB
            result = db_manager.documents_collection.delete_many({})
            logger.info(f"🧹 Cleared {result.deleted_count} documents from MongoDB")
            return True
            
    except Exception as e:
        logger.warning(f"⚠️ MongoDB clear failed: {e}, using fallback storage")
    
    # Fallback to in-memory storage
    global _fallback_documents
    count = len(_fallback_documents)
    _fallback_documents.clear()
    logger.info(f"🧹 Cleared {count} documents from fallback storage")
    return True

def get_database_status() -> Dict:
    """
    Get database connection status and statistics
    
    Returns:
        Dictionary with database status information
    """
    status = {
        "mongodb_connected": db_manager.is_connected(),
        "mongodb_url": Config.MONGODB_URL,
        "database_name": Config.MONGODB_DATABASE,
        "documents_count": get_documents_count(),
        "using_fallback": not db_manager.is_connected()
    }
    
    if db_manager.is_connected():
        try:
            # Get MongoDB server info
            server_info = db_manager.client.server_info()
            status["mongodb_version"] = server_info.get("version", "unknown")
        except:
            status["mongodb_version"] = "unknown"
    
    return status

# Cleanup function for graceful shutdown
def cleanup():
    """Cleanup database connections"""
    if db_manager:
        db_manager.close()