# 🏛️ DVC.AI Microservice Architecture

## 📁 New Structure Overview

Hệ thống đã được tổ chức lại theo kiến trúc microservice với các module rõ ràng và tách biệt trách nhiệm.

### 🎯 Benefits Achieved

- ✅ **Separation of Concerns**: Mỗi module có trách nhiệm riêng biệt
- ✅ **Modularity**: Dễ dàng thêm/sửa/xóa tính năng  
- ✅ **Maintainability**: Code organized, dễ debug và maintain
- ✅ **Scalability**: Có thể scale từng service riêng biệt
- ✅ **Testability**: Test từng module độc lập
- ✅ **Team Development**: Nhiều dev có thể làm việc song song

## 📦 Module Organization

### `app/` - Main Application Package
```
app/
├── __init__.py          # App package initialization
├── main.py             # FastAPI app configuration & ASGI setup
├── api/                # REST API endpoints (by feature)
│   ├── auth.py         # Authentication routes
│   ├── documents.py    # Document management routes  
│   ├── chatbot.py      # Chatbot interaction routes
│   ├── rag.py          # RAG system routes
│   └── websocket.py    # WebSocket status routes
├── core/               # Core business logic & utilities
│   ├── config.py       # Configuration management
│   ├── security.py     # Authentication & JWT handling
│   └── websocket.py    # WebSocket manager & events
├── models/             # Pydantic models for validation
│   ├── auth.py         # Authentication models
│   ├── documents.py    # Document models
│   ├── chatbot.py      # Chatbot models
│   └── rag.py          # RAG system models
├── services/           # External service integrations
│   ├── gcs_service.py  # Google Cloud Storage
│   ├── milvus_service.py # Vector database
│   ├── database.py     # MongoDB service
│   └── rag_service.py  # RAG pipeline service
├── utils/              # Utility functions
│   └── document_processor.py # Document processing utilities
└── workers/            # Background task workers
    ├── celery_app.py   # Celery configuration
    └── tasks.py        # Background task definitions
```

### `scripts/` - Standalone Scripts & Tools
```
scripts/
├── dev.py              # Development environment manager
├── setup_mongodb.py    # MongoDB setup & initialization
├── start_redis.py      # Redis startup script
├── start_worker.py     # Celery worker startup
├── load_documents_to_milvus.py # Milvus data loader
└── test_rag_system.py  # RAG system testing
```

### `docker/` - Container & Deployment Configs
```
docker/
├── docker-compose.yml          # Redis container
├── docker-compose-mongodb.yml  # MongoDB + Mongo Express
├── docker-compose-milvus.yml   # Milvus vector database
├── start_milvus.bat           # Milvus startup (Windows)
└── start_milvus.sh            # Milvus startup (Linux/macOS)
```

### `docs/` - Documentation
```
docs/
└── MILVUS_SETUP_GUIDE.md      # Milvus setup instructions
```

### `data/` - Data Storage
```
data/
└── uploads/                   # File upload storage
```

## 🔄 Import Strategy

### Relative Imports Within App Package
```python
# From API routes
from ..core.config import Config
from ..services.database import get_documents
from ..models.auth import LoginRequest

# From services
from ..core.config import Config
from ..utils.document_processor import DocumentProcessor

# From workers
from .celery_app import celery_app
from ..services.gcs_service import gcs_service
```

## 🚀 API Route Organization

### Feature-Based Routing
- **`/api/auth/*`**: Authentication & user management
- **`/api/documents/*`**: Document upload, management, deletion
- **`/api/rag/*`**: RAG queries, vector database stats
- **`/api/chatbot/*`**: Chatbot interactions
- **`/api/websocket/*`**: WebSocket connection status

### Model Validation
- Each API route has corresponding Pydantic models
- Request/response validation handled automatically
- Type safety across the application

## 🛠️ Running the Application

### Entry Point
```bash
cd be
python main.py
```

### With Scripts
```bash
# Start all services
python scripts/dev.py start

# Individual services
python scripts/start_redis.py
python scripts/setup_mongodb.py
python scripts/start_worker.py
```

### With Docker
```bash
# Start databases
docker-compose -f docker/docker-compose.yml up -d
docker-compose -f docker/docker-compose-mongodb.yml up -d
docker-compose -f docker/docker-compose-milvus.yml up -d

# Start workers
celery -A app.workers.celery_app.celery_app worker --loglevel=info --pool=threads --concurrency=2
```

## 🧪 Testing Strategy

### Module Testing
```bash
# Test individual components
python -m pytest app/api/test_auth.py
python -m pytest app/services/test_database.py
python -m pytest app/utils/test_document_processor.py

# Test RAG system
python scripts/test_rag_system.py
```

### Integration Testing
```bash
# Full system test
python scripts/dev.py test
```

## 📈 Migration Benefits

### Before (Monolithic)
- All code in single main.py file
- Mixed responsibilities
- Hard to test individual components
- Difficult team collaboration

### After (Microservice Style)
- Clear separation of concerns
- Feature-based organization
- Easy to test and maintain
- Scalable team development
- Professional code structure

## 🔮 Future Enhancements

### Easy to Add New Features
```python
# New API route
app/api/new_feature.py

# New models  
app/models/new_feature.py

# New service
app/services/new_feature_service.py
```

### Service Independence
- Each service can be developed independently
- Clear interfaces between modules
- Easy to mock dependencies for testing

---

**Architecture Version:** 3.1.0  
**Migration Date:** September 2025  
**Structure:** Microservice-style FastAPI application  
**Benefits:** Maintainable, Scalable, Professional**
