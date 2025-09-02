from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import uuid
from datetime import datetime, timedelta
import jwt
import hashlib
import json
import aiofiles
import socketio
import logging
from config import Config
from services.gcs_service import gcs_service
from websocket_manager import websocket_manager
from tasks import process_file_upload, process_bulk_upload

# Initialize logger
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Management API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Security configuration
security = HTTPBearer()
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM

# Local upload directory (temporary storage)
UPLOAD_DIR = Config.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: str
    size: int
    public_url: Optional[str] = None
    status: Optional[str] = None

class BulkUploadResponse(BaseModel):
    task_id: str
    message: str
    total_files: int

class FileUploadResponse(BaseModel):
    task_id: str
    message: str
    filename: str

# User database (demo users)
fake_users = {
    "admin": {
        "username": "admin",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "full_name": "Administrator",
        "role": "admin"
    }
}

# Import database functions
from database import get_documents, get_document_by_id
from database import delete_document as delete_document_from_db

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Routes
@app.get("/")
async def root():
    return {"message": "Document Management API is running"}

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = fake_users.get(request.username)
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": request.username})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    )

@app.get("/api/auth/me")
async def get_current_user(username: str = Depends(verify_token)):
    user = fake_users.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"]
    }

@app.post("/api/documents/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    username: str = Depends(verify_token)
):
    # Kiểm tra loại file
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Only {', '.join(Config.ALLOWED_EXTENSIONS)} files are allowed"
        )
    
    # Kiểm tra kích thước file
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    
    if file_size_mb > Config.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {Config.MAX_FILE_SIZE_MB}MB limit"
        )
    
    # Tạo tên file unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Lưu file tạm thời
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(content)
    
    # Tạo task ID
    task_id = str(uuid.uuid4())
    
    # Gửi task đến Celery queue
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

@app.get("/api/documents", response_model=List[DocumentInfo])
async def get_documents_endpoint(username: str = Depends(verify_token)):
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

@app.delete("/api/documents/{document_id}")
async def delete_document_endpoint(document_id: str, username: str = Depends(verify_token)):
    document = get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    filename = document.get("filename", "unknown")
    logger.info(f"🗑️ Starting deletion process for document: {filename} (ID: {document_id})")
    
    # Xóa file từ Google Cloud Storage nếu có
    public_url = document.get("public_url", "")
    gcs_deletion_success = True
    
    if public_url and public_url.startswith("gs://"):
        try:
            # Extract blob name từ GCS URL
            # Format: gs://bucket-name/path/to/file
            # Ví dụ: gs://my-bucket/documents/myfile.pdf -> documents/myfile.pdf
            blob_name = public_url.replace(f"gs://{gcs_service.bucket_name}/", "")
            
            logger.info(f"🌩️ Deleting file from GCS: {blob_name}")
            gcs_deletion_success = gcs_service.delete_file(blob_name)
            
            if gcs_deletion_success:
                logger.info(f"✅ Successfully deleted file from GCS: {blob_name}")
            else:
                logger.warning(f"⚠️ Failed to delete file from GCS: {blob_name}")
                
        except Exception as e:
            logger.error(f"❌ Error deleting file from GCS: {e}")
            gcs_deletion_success = False
    elif public_url and public_url.startswith("local://"):
        logger.info(f"📁 File stored locally, will delete from local storage")
    else:
        logger.info(f"ℹ️ No GCS URL found for document: {filename}")
    
    # Xóa file khỏi local disk nếu có
    local_deletion_success = True
    stored_filename = document.get("stored_filename", "")
    
    if stored_filename:
        file_path = os.path.join(UPLOAD_DIR, stored_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"✅ Successfully deleted local file: {file_path}")
            except Exception as e:
                logger.error(f"❌ Error deleting local file {file_path}: {e}")
                local_deletion_success = False
        else:
            logger.info(f"ℹ️ Local file not found: {file_path}")
    
    # Xóa khỏi MongoDB database
    database_deletion_success = delete_document_from_db(document_id)
    
    if database_deletion_success:
        logger.info(f"✅ Successfully deleted document from database: {filename} (ID: {document_id})")
        
        # Tạo response message tùy theo kết quả của từng bước
        messages = []
        if gcs_deletion_success or not public_url.startswith("gs://"):
            messages.append("Document deleted successfully")
        else:
            messages.append("Document deleted from database but failed to delete from cloud storage")
            
        if not local_deletion_success and stored_filename:
            messages.append("Warning: Could not delete local file")
        
        return {
            "message": "; ".join(messages),
            "details": {
                "document_id": document_id,
                "filename": filename,
                "database_deleted": True,
                "gcs_deleted": gcs_deletion_success if public_url.startswith("gs://") else "not_applicable",
                "local_deleted": local_deletion_success if stored_filename else "not_applicable"
            }
        }
    else:
        logger.error(f"❌ Failed to delete document from database: {filename} (ID: {document_id})")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete document from database. GCS deletion: {'success' if gcs_deletion_success else 'failed'}"
        )

@app.post("/api/documents/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    username: str = Depends(verify_token)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 50:  # Limit số lượng file
        raise HTTPException(status_code=400, detail="Maximum 50 files allowed per bulk upload")
    
    file_paths = []
    total_size = 0
    
    for file in files:
        # Kiểm tra loại file
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename}: Only {', '.join(Config.ALLOWED_EXTENSIONS)} files are allowed"
            )
        
        # Kiểm tra kích thước file
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        total_size += file_size_mb
        
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename}: Size exceeds {Config.MAX_FILE_SIZE_MB}MB limit"
            )
    
    # Kiểm tra tổng kích thước
    if total_size > Config.MAX_FILE_SIZE_MB * 10:  # 10x limit for bulk
        raise HTTPException(
            status_code=400,
            detail=f"Total size exceeds {Config.MAX_FILE_SIZE_MB * 10}MB limit"
        )
    
    # Lưu tất cả file tạm thời
    for file in files:
        await file.seek(0)  # Reset file pointer
        content = await file.read()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(content)
        
        file_paths.append({
            'path': file_path,
            'filename': file.filename
        })
    
    # Tạo bulk task ID
    bulk_task_id = str(uuid.uuid4())
    
    # Gửi bulk task đến Celery queue
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

@app.get("/api/websocket/status")
async def websocket_status(username: str = Depends(verify_token)):
    """Get WebSocket connection status"""
    user_sessions = websocket_manager.user_sessions.get(username, set())
    return {
        "connected": len(user_sessions) > 0,
        "session_count": len(user_sessions),
        "sessions": list(user_sessions)
    }

# Chatbot API
@app.post("/api/chatbot/message")
async def chatbot_message(
    message: dict,
    username: str = Depends(verify_token)
):
    return {
        "response": "Đây là phản hồi mẫu từ chatbot. Tính năng này sẽ được phát triển thêm trong tương lai.",
        "timestamp": datetime.now().isoformat()
    }

# Create combined ASGI app with WebSocket support
combined_asgi_app = socketio.ASGIApp(websocket_manager.sio, app)

if __name__ == "__main__":
    uvicorn.run(combined_asgi_app, host="0.0.0.0", port=8001)
