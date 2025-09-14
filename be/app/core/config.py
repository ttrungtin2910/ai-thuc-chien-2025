"""
Configuration Module

Centralized configuration management for the application.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dvc-ai-secret-key-change-in-production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))
    
    # File Upload Configuration
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    ALLOWED_EXTENSIONS = [
        ".pdf", ".docx", ".doc", ".txt", 
        ".png", ".jpg", ".jpeg", ".md"
    ]
    
    # Google Cloud Storage Configuration
    PROJECT_ID = os.getenv("PROJECT_ID", "")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Database Configuration
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "dvc_ai_db")
    
    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # WebSocket Configuration
    WEBSOCKET_CORS_ORIGINS = os.getenv("WEBSOCKET_CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Milvus Configuration
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    
    # OpenAI Configuration (Direct API)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))
    
    # Document Chunking Configuration (LangChain)
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "3000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    # LangChain separators in order of preference (most semantic to least)
    separators_raw = os.getenv("CHUNK_SEPARATORS", "\n\n|\n|. |? |! |; |: |\t| ")
    CHUNK_SEPARATORS = []
    
    # Parse separators using | as delimiter instead of comma to avoid conflicts
    for sep in separators_raw.split("|"):
        if sep.strip():  # Only add non-empty separators
            # Replace escape sequences
            processed_sep = sep.replace('\\n', '\n').replace('\\t', '\t')
            CHUNK_SEPARATORS.append(processed_sep)
    
    # Fallback if no separators parsed
    if not CHUNK_SEPARATORS:
        CHUNK_SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", "; ", ": ", "\t", " "]
    # Header preservation setting
    PRESERVE_HEADERS = os.getenv("PRESERVE_HEADERS", "true").lower() == "true"
    
    # API Configuration
    API_V1_PREFIX = "/api"
    APP_NAME = os.getenv("APP_NAME", "DVC.AI - Document Management")
    APP_VERSION = "3.1.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# Ensure upload directory exists
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
