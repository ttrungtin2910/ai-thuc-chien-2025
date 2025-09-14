"""
Document Management API Routes
"""

import os
import uuid
import aiofiles
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query

from ..models.documents import DocumentInfo, FileUploadResponse, BulkUploadResponse, DocumentDeleteResponse
from ..core.security import verify_token
from ..core.config import Config
from ..services.database import get_documents, get_document_by_id, delete_document as delete_document_from_db
from ..services.gcs_service import gcs_service
from ..services.milvus_service import MilvusService
from ..workers.tasks import process_file_upload, process_bulk_upload

router = APIRouter(prefix="/documents", tags=["documents"])

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Milvus service
milvus_service = MilvusService()


@router.get("/", response_model=List[DocumentInfo])
async def get_documents_endpoint(username: str = Depends(verify_token)):
    """Get all documents for the authenticated user"""
    documents = get_documents()
    return [
        DocumentInfo(
            id=doc["id"],
            filename=doc["filename"],
            file_type=doc["file_type"],
            upload_date=doc["upload_date"],
            size=doc["size"],
            public_url=doc.get("public_url"),
            status=doc.get("status")
        )
        for doc in documents
    ]


@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    username: str = Depends(verify_token)
):
    """Upload a single document"""
    # Check file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Only {', '.join(Config.ALLOWED_EXTENSIONS)} files are allowed"
        )
    
    # Check file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    
    if file_size_mb > Config.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {Config.MAX_FILE_SIZE_MB}MB limit"
        )
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(Config.UPLOAD_DIR, "uploads", unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save temporary file
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(content)
    
    # Create task ID
    task_id = str(uuid.uuid4())
    
    # Send task to Celery queue
    process_file_upload.delay(
        file_path=file_path,
        filename=file.filename,
        user_id=username,
        task_id=task_id
    )
    
    return FileUploadResponse(
        task_id=task_id,
        message="File upload started. You will receive real-time updates via WebSocket.",
        filename=file.filename
    )


@router.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    username: str = Depends(verify_token)
):
    """Upload multiple documents"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 50:  # Limit number of files
        raise HTTPException(status_code=400, detail="Maximum 50 files allowed per bulk upload")
    
    file_paths = []
    total_size = 0
    
    for file in files:
        # Check file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename}: Only {', '.join(Config.ALLOWED_EXTENSIONS)} files are allowed"
            )
        
        # Check file size
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        total_size += file_size_mb
        
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename}: Size exceeds {Config.MAX_FILE_SIZE_MB}MB limit"
            )
    
    # Check total size
    if total_size > Config.MAX_FILE_SIZE_MB * 10:  # 10x limit for bulk
        raise HTTPException(
            status_code=400,
            detail=f"Total size exceeds {Config.MAX_FILE_SIZE_MB * 10}MB limit"
        )
    
    # Save all files temporarily
    upload_dir = os.path.join(Config.UPLOAD_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        await file.seek(0)  # Reset file pointer
        content = await file.read()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(content)
        
        file_paths.append({
            'path': file_path,
            'filename': file.filename
        })
    
    # Create bulk task ID
    bulk_task_id = str(uuid.uuid4())
    
    # Send bulk task to Celery queue
    process_bulk_upload.delay(
        file_paths=file_paths,
        user_id=username,
        bulk_task_id=bulk_task_id
    )
    
    return BulkUploadResponse(
        task_id=bulk_task_id,
        message="Bulk upload started. You will receive real-time updates via WebSocket.",
        total_files=len(files)
    )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document_endpoint(document_id: str, username: str = Depends(verify_token)):
    """Delete a document"""
    document = get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    filename = document.get("filename", "unknown")
    
    # Delete file from Google Cloud Storage if exists
    public_url = document.get("public_url", "")
    gcs_deletion_success = True
    
    if public_url and public_url.startswith("gs://"):
        try:
            # Extract blob name from GCS URL
            blob_name = public_url.replace(f"gs://{gcs_service.bucket_name}/", "")
            gcs_deletion_success = gcs_service.delete_file(blob_name)
        except Exception:
            gcs_deletion_success = False
    
    # Delete file from local disk if exists
    local_deletion_success = True
    stored_filename = document.get("stored_filename", "")
    
    if stored_filename:
        file_path = os.path.join(Config.UPLOAD_DIR, "uploads", stored_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                local_deletion_success = False
    
    # Delete from database
    database_deletion_success = delete_document_from_db(document_id)
    
    if database_deletion_success:
        # Create response message based on deletion results
        messages = []
        if gcs_deletion_success or not public_url.startswith("gs://"):
            messages.append("Document deleted successfully")
        else:
            messages.append("Document deleted from database but failed to delete from cloud storage")
            
        if not local_deletion_success and stored_filename:
            messages.append("Warning: Could not delete local file")
        
        # Delete chunks from Milvus vector database
        milvus_deletion_success = False
        try:
            if milvus_service.connect():
                milvus_service.create_collection()
                milvus_deletion_success = milvus_service.delete_chunks_by_file(document["filename"])
                logger.info(f"🗑️ [DELETE] Milvus chunks deletion: {'✅ Success' if milvus_deletion_success else '❌ Failed'}")
        except Exception as e:
            logger.error(f"💥 [DELETE] Failed to delete Milvus chunks: {e}")
        
        return DocumentDeleteResponse(
            message="; ".join(messages),
            details={
                "document_id": document_id,
                "filename": filename,
                "database_deleted": True,
                "gcs_deleted": gcs_deletion_success if public_url.startswith("gs://") else "not_applicable",
                "local_deleted": local_deletion_success if stored_filename else "not_applicable",
                "milvus_deleted": milvus_deletion_success
            }
        )
    else:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete document from database. GCS deletion: {'success' if gcs_deletion_success else 'failed'}"
        )


@router.get("/chunks")
async def get_all_chunks(
    limit: int = Query(50, description="Number of chunks to return"),
    offset: int = Query(0, description="Number of chunks to skip"),
    file_name: str = Query(None, description="Filter by specific file name"),
    username: str = Depends(verify_token)
):
    """Get all chunks from Milvus vector database with pagination"""
    try:
        logger.info(f"🔍 [CHUNKS-API] Fetching chunks - limit={limit}, offset={offset}, file_name={file_name}")
        
        # Connect to Milvus if not connected
        if not milvus_service.connect():
            raise HTTPException(status_code=503, detail="Unable to connect to vector database")
        
        # Initialize collection
        milvus_service.create_collection()
        
        if file_name:
            # Get chunks for specific file
            chunks = milvus_service.get_chunks_by_file(file_name)
            result = {
                "chunks": chunks,
                "total": len(chunks),
                "retrieved": len(chunks),
                "limit": limit,
                "offset": 0,
                "has_more": False,
                "file_name": file_name
            }
        else:
            # Get all chunks with pagination
            result = milvus_service.get_all_chunks(limit=limit, offset=offset)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"✅ [CHUNKS-API] Retrieved {result['retrieved']} chunks (total: {result['total']})")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 [CHUNKS-API] Error fetching chunks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch chunks: {str(e)}")


@router.get("/chunks/stats")
async def get_chunks_stats(username: str = Depends(verify_token)):
    """Get statistics about chunks in Milvus"""
    try:
        logger.info("📊 [CHUNKS-STATS] Fetching chunk statistics")
        
        # Connect to Milvus if not connected
        if not milvus_service.connect():
            raise HTTPException(status_code=503, detail="Unable to connect to vector database")
        
        # Initialize collection
        milvus_service.create_collection()
        
        # Get basic stats
        total_chunks = milvus_service.get_collection_stats()
        
        # Get documents count from database
        documents = get_documents()
        total_documents = len(documents)
        
        # Group documents by file type
        file_types = {}
        for doc in documents:
            file_type = doc.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        stats = {
            "total_chunks": total_chunks,
            "total_documents": total_documents,
            "avg_chunks_per_document": round(total_chunks / total_documents, 2) if total_documents > 0 else 0,
            "file_types": file_types,
            "collection_name": milvus_service.collection_name,
            "milvus_connected": True
        }
        
        logger.info(f"📊 [CHUNKS-STATS] Stats: {total_chunks} chunks from {total_documents} documents")
        
        return stats
        
    except Exception as e:
        logger.error(f"💥 [CHUNKS-STATS] Error fetching stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


@router.post("/chunks/cleanup")
async def cleanup_orphaned_chunks(username: str = Depends(verify_token)):
    """Clean up orphaned chunks (chunks for files that no longer exist)"""
    try:
        logger.info("🧹 [CHUNKS-CLEANUP] Starting orphaned chunks cleanup")
        
        # Connect to Milvus
        if not milvus_service.connect():
            raise HTTPException(status_code=503, detail="Unable to connect to vector database")
        
        # Initialize collection
        milvus_service.create_collection()
        
        # Get current stats
        initial_count = milvus_service.get_collection_stats()
        logger.info(f"📊 [CHUNKS-CLEANUP] Initial chunks count: {initial_count}")
        
        if initial_count == 0:
            return {"message": "No chunks to clean up", "deleted": 0, "remaining": 0}
        
        # Get existing documents from database
        documents = get_documents()
        existing_files = set([doc["filename"] for doc in documents])
        logger.info(f"📁 [CHUNKS-CLEANUP] Found {len(existing_files)} files in database")
        
        # Get files from Milvus
        try:
            # Query all chunks to get file names
            results = milvus_service.collection.query(
                expr="chunk_id >= 0",
                output_fields=["file_name"],
                limit=10000
            )
        except:
            try:
                results = milvus_service.collection.query(
                    expr='file_name != ""',
                    output_fields=["file_name"],
                    limit=10000
                )
            except:
                results = milvus_service.collection.query(
                    expr="pk >= 0",
                    output_fields=["file_name"],
                    limit=10000
                )
        
        if not results:
            return {"message": "No chunks found in Milvus", "deleted": 0, "remaining": initial_count}
        
        # Get unique file names from Milvus
        milvus_files = set([r.get("file_name", "") for r in results if r.get("file_name")])
        logger.info(f"📁 [CHUNKS-CLEANUP] Found {len(milvus_files)} unique files in Milvus")
        
        # Find orphaned files
        orphaned_files = milvus_files - existing_files
        logger.info(f"🗑️ [CHUNKS-CLEANUP] Found {len(orphaned_files)} orphaned files")
        
        if not orphaned_files:
            return {
                "message": "No orphaned chunks found",
                "deleted": 0,
                "remaining": initial_count,
                "orphaned_files": []
            }
        
        # Delete chunks for orphaned files
        deleted_files = []
        failed_files = []
        
        for filename in orphaned_files:
            logger.info(f"🗑️ [CHUNKS-CLEANUP] Deleting chunks for: {filename}")
            try:
                success = milvus_service.delete_chunks_by_file(filename)
                if success:
                    deleted_files.append(filename)
                    logger.info(f"✅ [CHUNKS-CLEANUP] Successfully deleted chunks for: {filename}")
                else:
                    failed_files.append(filename)
                    logger.warning(f"❌ [CHUNKS-CLEANUP] Failed to delete chunks for: {filename}")
            except Exception as e:
                failed_files.append(filename)
                logger.error(f"💥 [CHUNKS-CLEANUP] Error deleting {filename}: {e}")
        
        # Get final stats
        final_count = milvus_service.get_collection_stats()
        deleted_count = initial_count - final_count
        
        logger.info(f"🎉 [CHUNKS-CLEANUP] Cleanup completed: {deleted_count} chunks deleted")
        
        return {
            "message": f"Cleanup completed: {deleted_count} chunks deleted for {len(deleted_files)} files",
            "initial_chunks": initial_count,
            "final_chunks": final_count,
            "deleted_chunks": deleted_count,
            "orphaned_files_found": len(orphaned_files),
            "files_processed": len(deleted_files),
            "files_failed": len(failed_files),
            "deleted_files": deleted_files,
            "failed_files": failed_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 [CHUNKS-CLEANUP] Error during cleanup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to cleanup chunks: {str(e)}")


@router.delete("/chunks/file/{file_name}")
async def delete_chunks_for_file(file_name: str, username: str = Depends(verify_token)):
    """Delete all chunks for a specific file (for testing)"""
    try:
        logger.info(f"🗑️ [CHUNKS-DELETE] Manual deletion request for file: {file_name}")
        
        # Connect to Milvus
        if not milvus_service.connect():
            raise HTTPException(status_code=503, detail="Unable to connect to vector database")
        
        # Initialize collection
        milvus_service.create_collection()
        
        # Get chunks count before deletion
        chunks_before = milvus_service.get_chunks_by_file(file_name)
        before_count = len(chunks_before)
        
        logger.info(f"📊 [CHUNKS-DELETE] Found {before_count} chunks for {file_name}")
        
        if before_count == 0:
            return {
                "message": f"No chunks found for file: {file_name}",
                "deleted": 0,
                "file_name": file_name
            }
        
        # Perform deletion
        success = milvus_service.delete_chunks_by_file(file_name)
        
        # Get chunks count after deletion
        chunks_after = milvus_service.get_chunks_by_file(file_name)
        after_count = len(chunks_after)
        deleted_count = before_count - after_count
        
        result = {
            "success": success,
            "file_name": file_name,
            "chunks_before": before_count,
            "chunks_after": after_count,
            "deleted": deleted_count,
            "message": f"{'Successfully' if success else 'Failed to'} delete {deleted_count} chunks for {file_name}"
        }
        
        logger.info(f"✅ [CHUNKS-DELETE] Result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"💥 [CHUNKS-DELETE] Error deleting chunks for {file_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete chunks: {str(e)}")
