from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from datetime import datetime, timedelta
import jwt
import hashlib
import json

app = FastAPI(title="Document Management API", version="1.0.0")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Thư mục lưu trữ file upload
UPLOAD_DIR = "uploads"
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

# Fake database cho demo
fake_users = {
    "admin": {
        "username": "admin",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "full_name": "Administrator",
        "role": "admin"
    }
}

fake_documents = []

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

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    username: str = Depends(verify_token)
):
    # Kiểm tra loại file
    allowed_extensions = ['.pdf', '.docx']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Tạo tên file unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Lưu file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Lưu thông tin document vào fake database
    document_info = {
        "id": f"doc_{len(fake_documents) + 1}",
        "filename": file.filename,
        "stored_filename": filename,
        "file_type": file_extension,
        "upload_date": datetime.now().isoformat(),
        "size": len(content),
        "uploaded_by": username
    }
    fake_documents.append(document_info)
    
    return {
        "message": "File uploaded successfully",
        "document": DocumentInfo(
            id=document_info["id"],
            filename=document_info["filename"],
            file_type=document_info["file_type"],
            upload_date=document_info["upload_date"],
            size=document_info["size"]
        )
    }

@app.get("/api/documents", response_model=List[DocumentInfo])
async def get_documents(username: str = Depends(verify_token)):
    return [
        DocumentInfo(
            id=doc["id"],
            filename=doc["filename"],
            file_type=doc["file_type"],
            upload_date=doc["upload_date"],
            size=doc["size"]
        )
        for doc in fake_documents
    ]

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, username: str = Depends(verify_token)):
    document = next((doc for doc in fake_documents if doc["id"] == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Xóa file khỏi disk
    file_path = os.path.join(UPLOAD_DIR, document["stored_filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Xóa khỏi fake database
    fake_documents.remove(document)
    
    return {"message": "Document deleted successfully"}

# Chatbot API (placeholder for future development)
@app.post("/api/chatbot/message")
async def chatbot_message(
    message: dict,
    username: str = Depends(verify_token)
):
    # Placeholder response
    return {
        "response": "Đây là phản hồi mẫu từ chatbot. Tính năng này sẽ được phát triển thêm trong tương lai.",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
