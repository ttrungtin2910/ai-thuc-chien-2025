# DVC.AI Backend - AI-Powered Document Management System

A comprehensive document management system with AI-powered content extraction and semantic search capabilities.

## ✨ Key Features

### 🤖 **AI-Powered Document Processing**
- **Multi-format support**: PDF, DOCX, TXT, Markdown, Images (PNG/JPG/JPEG)
- **Smart content extraction**: Automatic text extraction from all file types
- **AI Vision analysis**: GPT-4V for image content analysis and OCR
- **Intelligent chunking**: Optimized content splitting for vector search

### 🗄️ **Vector Database Integration**
- **Semantic search**: OpenAI embeddings with Milvus vector database
- **Real-time indexing**: Automatic content indexing on file upload
- **Smart retrieval**: Context-aware document search and RAG capabilities

### ⚡ **Real-time Processing**
- **WebSocket updates**: Live progress tracking during file processing
- **Async processing**: Celery-based background task processing
- **Multi-stage workflow**: Extract → Upload → Index → Store

## 🚀 Quick Setup

```bash
# Complete setup (recommended)
python setup.py

# Install dependencies only
python setup.py --deps

# Start services only
python setup.py --start

# Stop all services
python setup.py --stop

# Show service status
python setup.py --status

# Show help
python setup.py --help
```

## 📋 Prerequisites

### Required Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### System Dependencies (for image processing)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-vie

# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

# macOS
brew install tesseract tesseract-lang
```

## ⚙️ Configuration

### 1. Environment Variables
Create `.env` file with the following:
```bash
# OpenAI Configuration (Required for AI features)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4o

# Milvus Configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Google Cloud Storage (Optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
PROJECT_ID=your_project_id
GCS_BUCKET_NAME=your_bucket_name

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=dvc_ai_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 2. Start Required Services
```bash
# Start Milvus (Docker)
docker run -d --name milvus-standalone \
  -p 19530:19530 -p 9091:9091 \
  -v milvus_data:/var/lib/milvus \
  milvusdb/milvus:latest standalone

# Start Redis
redis-server

# Start MongoDB (if not using Docker)
mongod
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Terminal 1: Start Celery worker for background processing
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 2: Start FastAPI server
python main.py

# Terminal 3: Load sample documents (optional)
python scripts/load_documents_to_milvus.py
```

### Production Mode
```bash
# Start all services
python setup.py --start
```

## 📊 Services & Endpoints

- **API Server**: http://localhost:8001
- **MongoDB**: localhost:27017  
- **Redis**: localhost:6379
- **Milvus Vector DB**: localhost:19530
- **Mongo Express**: http://localhost:8081 (admin/admin123)
- **Attu (Milvus UI)**: http://localhost:3001

### Key API Endpoints
```bash
# Document Upload
POST /api/documents/upload
POST /api/documents/bulk-upload

# Document Management  
GET /api/documents/
DELETE /api/documents/{id}

# RAG & Search
POST /api/rag/chat
POST /api/rag/search
```

## 🔄 Document Processing Workflow

1. **File Upload** → User uploads file via web interface
2. **Content Extraction** → AI extracts text from PDF/images using OCR + GPT-4V
3. **Cloud Storage** → File saved to Google Cloud Storage (optional)
4. **Vector Processing** → Content chunked and converted to embeddings
5. **Database Storage** → Vectors saved to Milvus, metadata to MongoDB
6. **Search Ready** → Content available for semantic search

## 🧪 Testing

### Test Document Processing
```bash
# Create a test file
echo "This is a test document for AI processing." > test.txt

# Upload via API
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.txt" \
  http://localhost:8001/api/documents/upload

# Test search functionality
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "test document", "top_k": 5}' \
  http://localhost:8001/api/rag/search
```

## 📁 Project Structure

```
be/
├── app/                    # Main application code
│   ├── api/               # FastAPI routes
│   ├── services/          # Business logic services
│   ├── utils/             # Document processing utilities
│   ├── workers/           # Celery background tasks
│   ├── models/            # Data models
│   └── core/              # Core configurations
├── scripts/               # Utility scripts
├── database/              # Database credentials
├── data/                  # Sample data
├── setup.py              # Main setup script
├── requirements.txt      # Python dependencies
└── .env                  # Environment configuration
```

## 🐛 Troubleshooting

### Common Issues

**OpenAI API Issues:**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Milvus Connection Issues:**
```bash
# Check if Milvus is running
docker ps | grep milvus

# Check Milvus logs
docker logs milvus-standalone

# Verify port availability
netstat -an | grep 19530
```

**File Processing Issues:**
- Ensure Tesseract OCR is installed for image processing
- Check file format is supported: PDF, DOCX, TXT, MD, PNG, JPG, JPEG
- Verify file size is under 100MB limit

### Performance Tips
- Use bulk upload for multiple files
- Monitor memory usage for large files
- Consider image compression for large images
- Use appropriate chunk sizes for your content type

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
