# 🌍 DVC.AI - Hướng dẫn hoàn chỉnh

## 🎯 Tổng quan dự án

**DVC.AI** (Trợ lý dịch vụ công và cổng Kiến thức) là hệ thống quản lý tài liệu thông minh với thiết kế theme **Mệnh Thổ** ấm áp, sử dụng AI để hỗ trợ dịch vụ công.

### 🚀 Tính năng chính
- ✅ **Đăng nhập bảo mật** với JWT authentication
- ✅ **Quản lý tài liệu** - Upload, xem, xóa file PDF và DOCX
- ✅ **Chatbot hỗ trợ** - Tương tác với trợ lý ảo
- ✅ **Upload đồng loạt** - Hỗ trợ nhiều file cùng lúc với progress tracking
- ✅ **WebSocket real-time** - Theo dõi tiến trình upload (Socket.IO)
- ✅ **Google Cloud Storage** - Lưu trữ file trên cloud (uniform bucket access)
- ✅ **Celery Background Tasks** - Xử lý background tương thích Windows
- ✅ **UI/UX hiện đại** - Font MaisonNeue, thiết kế responsive
- ✅ **Milvus Vector Database** - Vector search cho RAG
- ✅ **RAG System** - Retrieval-Augmented Generation với OpenAI API
- ✅ **Microservice Architecture** - Cấu trúc module hóa, dễ bảo trì

### 🏗️ Kiến trúc hệ thống (Microservice Style)
- **Frontend:** ReactJS + Custom CSS + MaisonNeue font
- **Backend:** Python FastAPI (Microservice Architecture) + Celery (threads pool) + Redis
- **Database:** MongoDB với fallback in-memory storage
- **Vector Database:** Milvus cho RAG và semantic search
- **Storage:** Google Cloud Storage + Local uploads
- **Authentication:** JWT tokens với centralized security module
- **Real-time:** WebSocket + Socket.IO (ASGI integrated)
- **AI/ML:** OpenAI API (Direct) + RAG Pipeline + Vector Search
- **Environment:** Windows-compatible với Conda
- **Architecture:** Modular design với separation of concerns

## 📁 Cấu trúc dự án (Microservice Architecture)

```
d:\02-VLU\02-AI-ThucChien\
├── be/                     # Backend FastAPI (Microservice Style)
│   ├── main.py            # Application entry point
│   ├── app/               # Main application package
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI app configuration
│   │   ├── api/           # API routes (separated by feature)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py    # Authentication routes
│   │   │   ├── documents.py # Document management routes
│   │   │   ├── chatbot.py # Chatbot routes
│   │   │   ├── rag.py     # RAG (AI) routes
│   │   │   └── websocket.py # WebSocket routes
│   │   ├── core/          # Core business logic & utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py  # Configuration management
│   │   │   ├── security.py # Authentication & JWT
│   │   │   └── websocket.py # WebSocket manager
│   │   ├── models/        # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── auth.py    # Auth models
│   │   │   ├── documents.py # Document models
│   │   │   ├── chatbot.py # Chatbot models
│   │   │   └── rag.py     # RAG models
│   │   ├── services/      # External services integration
│   │   │   ├── __init__.py
│   │   │   ├── gcs_service.py # Google Cloud Storage
│   │   │   ├── milvus_service.py # Vector database
│   │   │   ├── database.py # MongoDB service
│   │   │   └── rag_service.py # RAG service
│   │   ├── utils/         # Utility functions
│   │   │   ├── __init__.py
│   │   │   └── document_processor.py # Document processing
│   │   └── workers/       # Background task workers
│   │       ├── __init__.py
│   │       ├── celery_app.py # Celery configuration
│   │       └── tasks.py   # Background tasks
│   ├── scripts/           # Standalone scripts & tools
│   │   ├── __init__.py
│   │   ├── dev.py         # Development manager
│   │   ├── setup_mongodb.py # MongoDB setup
│   │   ├── start_redis.py # Redis startup
│   │   ├── start_worker.py # Worker startup
│   │   ├── load_documents_to_milvus.py # Milvus loader
│   │   └── test_rag_system.py # RAG testing
│   ├── docker/            # Docker & deployment configs
│   │   ├── docker-compose.yml # Redis
│   │   ├── docker-compose-mongodb.yml # MongoDB
│   │   ├── docker-compose-milvus.yml # Milvus Vector DB
│   │   ├── start_milvus.bat # Milvus startup (Windows)
│   │   └── start_milvus.sh # Milvus startup (Linux/macOS)
│   ├── docs/              # Documentation
│   │   └── MILVUS_SETUP_GUIDE.md # Milvus setup guide
│   ├── data/              # Data storage
│   │   └── uploads/       # File uploads
│   ├── database/          # Database credentials
│   ├── requirements.txt   # Python dependencies
│   ├── environment.yml    # Conda environment
│   └── env.example        # Environment template
├── fe/                     # Frontend ReactJS
│   ├── public/
│   │   ├── fonts/         # MaisonNeue fonts
│   │   ├── fonts.css      # Font configuration
│   │   └── index.html
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── assets/        # Images & icons
│   ├── package.json
│   └── build/             # Production build
└── data/                   # Global data directory
    └── thutuccongdan/     # Document corpus for RAG
```

## 🎨 Thiết kế Theme Mệnh Thổ

### 🌍 Bảng màu chính
```css
--primary-color: #D2691E;        /* Cam đất chocolate - ấm áp, tin cậy */
--primary-light: #DEB887;        /* Vàng đất burlywood - nhẹ nhàng */
--primary-dark: #A0522D;         /* Nâu đất sienna - ổn định */
--secondary-color: #FDF5E6;      /* Be kem old lace - thanh nhã */
--accent-color: #CD853F;         /* Vàng đất sandy brown - nổi bật */
--border-color: #F4E4BC;         /* Màu lúa mì nhạt - tinh tế */
```

### 🥁 Biểu tượng Trống đồng Đông Sơn
- **Logo chính**: Icon 64x64px trên màn hình login
- **Header**: Icon 40x40px màu trắng
- **Background**: Pattern 800x800px với opacity thấp
- **Ý nghĩa**: Kết nối truyền thống văn hóa với công nghệ AI

### 🔤 Typography - MaisonNeue
- **Font chính**: MaisonNeue (6 weights từ Thin đến Bold)
- **Fallback**: Inter từ Google Fonts
- **Font stack**: `'MaisonNeue', 'Inter', -apple-system, sans-serif`

## 🏛️ Microservice Architecture Benefits

### ✨ Tính năng mới (Version 3.1.0)
- **🎯 Separation of Concerns**: Mỗi module có trách nhiệm riêng biệt
- **📦 Modularity**: Dễ dàng thêm/sửa/xóa tính năng
- **🔧 Maintainability**: Code organized, dễ debug và maintain
- **🚀 Scalability**: Có thể scale từng service riêng biệt
- **🧪 Testability**: Test từng module độc lập
- **👥 Team Development**: Nhiều dev có thể làm việc song song

### 📋 Module Organization
- **`app/api/`**: REST API endpoints, organized by feature
- **`app/core/`**: Core business logic, configuration, security
- **`app/models/`**: Pydantic models for validation
- **`app/services/`**: External service integrations (GCS, Milvus, DB)
- **`app/utils/`**: Utility functions and helpers
- **`app/workers/`**: Background task workers
- **`scripts/`**: Standalone maintenance scripts
- **`docker/`**: Container and deployment configs
- **`docs/`**: Documentation and guides

### 🔄 Import Strategy
```python
# Relative imports within app package
from ..core.config import Config
from ..services.database import get_documents
from ..models.auth import LoginRequest
```

## 🛠️ Cài đặt và Chạy

### Bước 1: Setup Backend (FastAPI)

```bash
# Di chuyển vào thư mục backend
cd be

# Tạo môi trường Conda (khuyến nghị)
conda env create -f environment.yml
conda activate document-management-be

# Hoặc sử dụng pip
pip install -r requirements.txt

# Cấu hình environment
cp env.example .env
# Chỉnh sửa .env với thông tin Google Cloud và JWT
```

### Bước 2: Setup Frontend (ReactJS)

```bash
# Mở terminal mới, di chuyển vào thư mục frontend
cd fe

# Cài đặt dependencies
npm install
```

### Bước 3: Chạy hệ thống

#### Cách 1: Quick Start với Development Manager (Khuyến nghị)
```bash
cd be
python scripts/dev.py start
```

#### Cách 2: Manual Start từng service
```bash
# Terminal 1: Start Redis
cd be
python scripts/start_redis.py

# Terminal 2: Start MongoDB
cd be
python scripts/setup_mongodb.py

# Terminal 3: Start Celery Worker
cd be
python scripts/start_worker.py

# Terminal 4: Start Backend API
cd be
python main.py

# Terminal 5: Start Frontend
cd fe
npm start
```

#### Cách 3: Docker Compose (Alternative)
```bash
# Terminal 1: Start Redis và MongoDB
cd be
docker-compose -f docker/docker-compose.yml up -d redis
docker-compose -f docker/docker-compose-mongodb.yml up -d

# Terminal 2: Start Celery Worker
cd be
celery -A app.workers.celery_app.celery_app worker --loglevel=info --pool=threads --concurrency=2

# Terminal 3: Start Backend API
cd be
python main.py

# Terminal 4: Start Frontend
cd fe
npm start
```

### Bước 4: Truy cập ứng dụng

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **WebSocket**: ws://localhost:8001/ws

### Tài khoản mặc định
- **Username:** `admin`
- **Password:** `password123`

## 🔧 Cấu hình nâng cao

### Environment Variables (Backend)
```bash
# JWT Security
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256

# Google Cloud Configuration
PROJECT_ID=your-google-cloud-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
GCS_BUCKET_NAME=your-bucket-name

# MongoDB Configuration (Optional - fallback to in-memory if not available)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=dvc_ai_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Upload Configuration
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=.pdf,.docx,.doc,.txt,.png,.jpg,.jpeg

# WebSocket Configuration
WEBSOCKET_CORS_ORIGINS=http://localhost:3000
```

### Environment Variables (Frontend)
```env
REACT_APP_API_URL=http://localhost:8001
REACT_APP_APP_NAME=DVC.AI
```

## 🗄️ MongoDB Setup (Recommended)

### 🐳 Option 1: Docker MongoDB (Khuyến nghị)

**Yêu cầu:** Docker & Docker Compose đã cài đặt

```bash
# 1. Start MongoDB với Docker
cd be
docker-compose -f docker-compose-mongodb.yml up -d

# 2. Verify MongoDB đang chạy
docker ps | grep mongodb

# 3. Test connection
python -c "from database import get_database_status; print(get_database_status())"

# 4. Stop MongoDB (khi cần)
docker-compose -f docker-compose-mongodb.yml down
```

**Tính năng Docker MongoDB:**
- ✅ **Isolated environment** - Không ảnh hưởng system
- ✅ **Data persistence** - Volume mount `/data/db`
- ✅ **Web admin interface** - Mongo Express tại http://localhost:8081
- ✅ **Health checks** - Auto-restart nếu unhealthy
- ✅ **Easy cleanup** - `docker-compose down -v`

**Mongo Express Admin Panel:**
- 🌐 **URL:** http://localhost:8081
- 👤 **Username:** admin
- 🔐 **Password:** admin123
- 📊 **Database:** dvc_ai_db

### 💻 Option 2: Native Installation

**Windows:**
```bash
# Option 1: Download from official site
# https://www.mongodb.com/try/download/community

# Option 2: Using Chocolatey
choco install mongodb

# Start MongoDB service
net start MongoDB
```

**macOS:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Kiểm tra MongoDB
```bash
# Test MongoDB setup với script
cd be
python setup_mongodb.py

# Test MongoDB connection
python -c "from database import get_database_status; print(get_database_status())"

# Check Docker containers
docker ps | grep mongodb
```

### Tính năng MongoDB
- ✅ **Persistent storage** - Documents được lưu vĩnh viễn
- ✅ **Scalability** - Dễ dàng scale với MongoDB cluster
- ✅ **Performance** - Indexed queries for faster retrieval
- ✅ **Backup & Recovery** - MongoDB built-in backup tools
- ✅ **Fallback mechanism** - Auto-fallback to in-memory nếu MongoDB không available

### Không có MongoDB?
Không sao! Hệ thống tự động fallback về **in-memory storage**:
- ✅ Application vẫn hoạt động bình thường
- ⚠️ Documents sẽ mất khi restart server
- 💡 Suitable cho development và testing

### 🎯 Quick Start với Development Scripts
```bash
# 1. Clone project và cd vào backend
cd be

# 2. Start MongoDB với setup script
python setup_mongodb.py

# 3. Start Redis
python start_redis.py

# 4. Start backend server
python main.py

# 5. Start frontend (terminal mới)
cd ../fe
npm start
```

### 🚀 Super Quick Start (All-in-One)
```bash
# 1. Clone project và cd vào backend
cd be

# 2. Start tất cả services với dev manager
python dev.py start

# 3. Start frontend (terminal mới)
cd ../fe
npm start
```

### 🔧 Docker MongoDB Management
```bash
# Xem status containers
docker ps | grep mongodb

# Xem logs MongoDB
docker-compose -f docker-compose-mongodb.yml logs mongodb

# Restart MongoDB
docker-compose -f docker-compose-mongodb.yml restart mongodb

# Stop MongoDB
docker-compose -f docker-compose-mongodb.yml down

# Reset database (xóa tất cả data)
docker-compose -f docker-compose-mongodb.yml down -v

# View database với Mongo Express
# http://localhost:8081 (admin/admin123)
```

### 🔐 Production MongoDB Security
Cho production, enable authentication trong `docker-compose-mongodb.yml`:
```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: admin
  MONGO_INITDB_ROOT_PASSWORD: your-secure-password
  MONGO_INITDB_DATABASE: dvc_ai_db
```

Và update `config.py`:
```python
MONGODB_URL = "mongodb://admin:your-secure-password@localhost:27017"
```

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile */
@media (max-width: 767px)

/* Tablet */  
@media (min-width: 768px) and (max-width: 991px)

/* Small Desktop */
@media (min-width: 992px) and (max-width: 1199px)

/* Desktop */
@media (min-width: 1200px) and (max-width: 1919px)
- max-width: 1200px, centered

/* Large Desktop/2K */
@media (min-width: 1920px) and (max-width: 2559px)
- max-width: 1600px, centered

/* 4K+ Ultra Wide */
@media (min-width: 2560px)
- max-width: 1800px, centered
```

### Spacing System
- **Base unit**: 8px
- **Margins**: .mb-0 to .mb-5 (0px to 40px)
- **Paddings**: .p-0 to .p-5 (0px to 40px)
- **Gaps**: .gap-1 to .gap-4 (8px to 32px)

## 📋 API Documentation (Microservice Structure)

### Authentication (`app/api/auth.py`)
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Lấy thông tin user

### Document Management (`app/api/documents.py`)
- `GET /api/documents/` - Lấy danh sách tài liệu
- `POST /api/documents/upload` - Upload tài liệu đơn lẻ
- `POST /api/documents/bulk-upload` - Upload nhiều tài liệu
- `DELETE /api/documents/{id}` - Xóa tài liệu

### RAG System (`app/api/rag.py`)
- `POST /api/rag/query` - Query RAG system với câu hỏi
- `GET /api/rag/stats` - Thống kê vector database
- `POST /api/rag/connect` - Kết nối đến Milvus

### WebSocket (`app/api/websocket.py`)
- `GET /api/websocket/status` - Trạng thái kết nối WebSocket
- **Events**: `file_upload_progress`, `file_upload_complete`, `bulk_upload_progress`

### Chatbot (`app/api/chatbot.py`)
- `POST /api/chatbot/message` - Gửi tin nhắn đến chatbot

### API Models
- **Auth Models**: `app/models/auth.py`
- **Document Models**: `app/models/documents.py`
- **RAG Models**: `app/models/rag.py`
- **Chatbot Models**: `app/models/chatbot.py`

## 🚀 Deployment

### Backend Deployment
```bash
# Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Using Docker
docker build -t dvc-ai-backend .
docker run -p 8000:8000 dvc-ai-backend
```

### Frontend Deployment
```bash
# Build production
npm run build

# Serve with nginx/apache
# Copy build/ folder to web server
```

### Production Environment
- Sử dụng Redis cluster thay vì Docker container
- Cấu hình Google Cloud Storage production bucket
- Setup monitoring và logging
- SSL/TLS certificates
- Load balancing nếu cần

## 🐛 Troubleshooting

### Backend không start được
```bash
# Kiểm tra Python version
python --version  # Cần >= 3.8

# Kiểm tra dependencies
pip list

# Kiểm tra port 8001
netstat -an | grep 8001

# Kiểm tra Redis connection
docker exec -it dvc-ai-redis redis-cli ping
```

### Frontend không kết nối được backend
```bash
# Kiểm tra backend đang chạy
curl http://localhost:8001

# Kiểm tra CORS configuration
# Xem console browser để debug
```

### File upload lỗi
- Kiểm tra file format (chỉ PDF, DOCX, DOC, TXT, PNG, JPG, JPEG)
- Kiểm tra file size (< 100MB)
- Kiểm tra quyền write vào thư mục uploads/
- Kiểm tra Google Cloud Storage credentials

### WebSocket connection issues
- Kiểm tra CORS origins trong .env
- Verify frontend connects to correct URL
- Check browser console for connection errors
- Ensure Socket.IO versions compatibility

## 📊 Performance & Monitoring

### Redis Monitoring
```bash
# Check Redis status
docker exec -it dvc-ai-redis redis-cli info

# Monitor memory usage
docker exec -it dvc-ai-redis redis-cli info memory

# View Redis logs
docker compose logs redis
```

### Celery Monitoring
```bash
# Check worker status
celery -A celery_app.celery_app status

# View active tasks
celery -A celery_app.celery_app inspect active

# Monitor task queue
celery -A celery_app.celery_app inspect registered
```

### System Performance
- Monitor file upload speeds
- Track WebSocket connection stability
- Monitor Google Cloud Storage usage
- Check system resource utilization

## 🔒 Security Considerations

### JWT Security
- Sử dụng strong secret keys
- Rotate credentials regularly
- Implement token expiration
- Validate token claims

### File Upload Security
- File type validation
- File size limits
- Virus scanning (recommended)
- Secure file storage

### API Security
- Rate limiting
- Input validation
- CORS configuration
- HTTPS enforcement

## 🚀 Version 3.1.0 - Microservice Architecture & RAG System

### ✨ New Features (Version 3.1.0):

1. **🏛️ Microservice Architecture**
   - **Modular design**: Tách biệt API routes, models, services
   - **Separation of concerns**: Mỗi module có trách nhiệm riêng
   - **Easy maintenance**: Code structure rõ ràng, dễ debug
   - **Scalable development**: Team có thể làm việc song song

2. **🤖 RAG (Retrieval-Augmented Generation)**
   - **Milvus Vector Database**: Vector search với embedding model
   - **OpenAI API Integration**: GPT-4o cho text generation, text-embedding-3-large cho embeddings
   - **Document Processing**: Chunk documents thành vectors
   - **Intelligent Q&A**: Semantic search + AI generation

3. **📦 Enhanced Service Organization**
   - **app/api/**: API routes organized by feature
   - **app/core/**: Core logic, config, security
   - **app/services/**: External service integrations
   - **scripts/**: Maintenance và setup tools
   - **docker/**: Container configurations

4. **🔧 Advanced Features**
   - **Vector Database**: Milvus with Docker setup
   - **Document Corpus**: Thủ tục công dân dataset
   - **RAG Pipeline**: End-to-end question answering
   - **Microservice APIs**: RESTful endpoints for each service

### 🛠️ Technical Stack Updates:
- **Architecture**: Microservice-style FastAPI application
- **Database**: MongoDB 7.0 (primary) + In-memory (fallback)
- **Vector Database**: Milvus 2.3.3 với Docker Compose
- **AI/ML**: OpenAI API (GPT-4o + text-embedding-3-large)
- **Containerization**: Docker Compose cho full stack
- **Process Management**: Celery workers với threads pool
- **Real-time**: Enhanced WebSocket integration
- **Code Organization**: Modular imports với relative paths

## 🔧 Các vấn đề đã sửa và cải tiến

### ✅ Lỗi đã khắc phục (September 2025):

1. **Celery Worker Error trên Windows**
   - **Lỗi**: `ValueError: not enough values to unpack (expected 3, got 0)`
   - **Nguyên nhân**: Prefork pool không tương thích Windows
   - **Giải pháp**: Sử dụng threads pool (`worker_pool='threads'`)

2. **WebSocket 403 Forbidden**
   - **Lỗi**: `connection rejected (403 Forbidden)`
   - **Nguyên nhân**: CORS configuration và ASGI integration
   - **Giải pháp**: Cập nhật CORS và sử dụng `socketio.ASGIApp()`

3. **Google Cloud Storage ACL Error**
   - **Lỗi**: `Cannot get legacy ACL when uniform bucket-level access enabled`
   - **Nguyên nhân**: GCS policy mới
   - **Giải pháp**: Loại bỏ `blob.make_public()`, dùng uniform access

4. **Threading Conflicts trong Tasks**
   - **Lỗi**: AsyncIO conflicts trong sync context
   - **Giải pháp**: Simplified WebSocket helper function

### 🚀 Cải tiến mới:

- **Windows Compatibility**: Tối ưu hóa cho môi trường Windows
- **Conda Environment**: Hướng dẫn sử dụng conda cho stability
- **Real-time Progress**: WebSocket tracking cho file uploads
- **Modern UI**: Font MaisonNeue và responsive design

## 🛠️ Troubleshooting

### Lỗi thường gặp:

**1. Celery Worker không start được:**
```bash
# Đảm bảo đang trong conda environment
conda activate document-management-be
cd be
python start_worker.py

# Kiểm tra output phải có: "2 (thread)" NOT "(prefork)"
```

**2. WebSocket không kết nối được:**
```bash
# Kiểm tra backend logs xem có "connection open"
# Frontend console không có lỗi CORS
```

**3. Redis connection failed:**
```bash
# Start Redis với script
python start_redis.py

# Test connection
python -c "import redis; print(redis.Redis().ping())"
```

**4. MongoDB không kết nối được:**
```bash
# Setup MongoDB với script
python setup_mongodb.py

# Test connection
python -c "from database import get_database_status; print(get_database_status())"
```

## 📈 Tính năng sẽ phát triển

- [ ] **Database integration** (PostgreSQL/MongoDB)
- [ ] **File preview** cho PDF và DOCX
- [ ] **Advanced search** và filtering
- [ ] **User management** và phân quyền
- [ ] **Document versioning**
- [ ] **Email notifications**
- [ ] **Advanced chatbot** với AI/NLP
- [ ] **Audit logs** và reporting
- [ ] **Multi-language support**
- [ ] **Dark mode** theme
- [ ] **Mobile app** (React Native)

## 📞 Hỗ trợ

- **Email:** support@domain.gov.vn
- **Hotline:** 1900-xxxx
- **Documentation:** http://localhost:8001/docs
- **GitHub Issues:** [Repository URL]

## 📄 License

MIT License - Xem file LICENSE để biết chi tiết.

---

**Phiên bản:** 3.2.0 (OpenAI Integration & Production Ready)  
**Cập nhật:** September 2025  
**Tác giả:** AI Assistant  
**Status:** ✅ Microservice Architecture + RAG + OpenAI API Integration complete  
**Features:** Microservices, RAG, Milvus Vector DB, OpenAI API, Modular Design  
**Compatibility:** Windows + Docker + Conda optimized  
**Brand:** DVC.AI - Intelligent Document Management with OpenAI Integration**
