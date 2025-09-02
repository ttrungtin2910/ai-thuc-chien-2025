"""
Document Management API Routes
"""

import os
import uuid
import aiofiles
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File

from ..models.documents import DocumentInfo, FileUploadResponse, BulkUploadResponse, DocumentDeleteResponse
from ..core.security import verify_token
from ..core.config import Config
from ..services.database import get_documents, get_document_by_id, delete_document as delete_document_from_db
from ..services.gcs_service import gcs_service
from ..workers.tasks import process_file_upload, process_bulk_upload

router = APIRouter(prefix="/documents", tags=["documents"])


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
        
        return DocumentDeleteResponse(
            message="; ".join(messages),
            details={
                "document_id": document_id,
                "filename": filename,
                "database_deleted": True,
                "gcs_deleted": gcs_deletion_success if public_url.startswith("gs://") else "not_applicable",
                "local_deleted": local_deletion_success if stored_filename else "not_applicable"
            }
        )
    else:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete document from database. GCS deletion: {'success' if gcs_deletion_success else 'failed'}"
        )
