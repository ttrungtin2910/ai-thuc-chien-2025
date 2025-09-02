import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # JWT Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    
    # Google Cloud Configuration
    PROJECT_ID = os.getenv("PROJECT_ID")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    
    # MongoDB Configuration
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "dvc_ai_db")
    
    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Upload Configuration
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", ".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg").split(",")
    
    # WebSocket Configuration
    WEBSOCKET_CORS_ORIGINS = os.getenv("WEBSOCKET_CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Local upload directory
    UPLOAD_DIR = "uploads"
