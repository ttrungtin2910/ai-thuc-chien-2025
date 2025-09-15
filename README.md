# 🚀 DVC.AI - Virtual Assistant Platform

DVC.AI là một nền tảng trợ lý ảo thông minh được xây dựng với kiến trúc microservices, tích hợp các công nghệ AI tiên tiến để cung cấp dịch vụ hỗ trợ công dân trong các thủ tục hành chính.

## ✨ **Tính năng chính**

### 🤖 **AI-Powered Document Processing**
- **Multi-format support**: PDF, DOCX, TXT, Markdown, Images (PNG/JPG/JPEG)
- **Smart content extraction**: Tự động trích xuất nội dung từ mọi loại file
- **AI Vision analysis**: GPT-4V phân tích hình ảnh và OCR thông minh
- **Intelligent chunking**: Tối ưu phân chia nội dung cho vector search

### 📚 **Advanced RAG System**
- **Semantic search**: OpenAI embeddings với Milvus vector database
- **Real-time indexing**: Tự động index nội dung khi upload file
- **Context-aware retrieval**: Tìm kiếm thông tin chính xác với ngữ cảnh

### ⚡ **Real-time Processing**
- **WebSocket updates**: Theo dõi tiến trình upload real-time
- **Background processing**: Celery xử lý bất đồng bộ
- **Multi-stage workflow**: Extract → Upload → Index → Store

### 🏗️ **System Architecture**
- **Microservices**: Kiến trúc tách biệt, dễ scale
- **Docker**: Triển khai container hóa hoàn toàn  
- **Vector Database**: Milvus để lưu trữ và tìm kiếm embeddings

---

## 🚀 **Khởi động nhanh** 

### **1-Command Setup (Recommended):**
```bash
# Ubuntu/Linux
git clone <repository-url>
cd dvc-ai-project
cd deps && chmod +x docker-build.sh && ./docker-build.sh
```

```cmd
# Windows  
git clone <repository-url>
cd dvc-ai-project
cd deps && python setup.py
```

**➡️ Truy cập:** 
- **Development:** http://localhost:8080 (khuyên dùng - không cần admin)
- **Production:** http://dvc.ink (sau khi deploy)
- **Classic:** http://localhost:3000

### **Prerequisites:**
- Docker Desktop >= 20.0
- OpenAI API Key ([Get here](https://platform.openai.com/api-keys))
- 4GB RAM, 20GB disk space

### **Configuration:**
```bash
# Tạo file .env với cấu hình cần thiết
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
echo "OPENAI_EMBEDDING_MODEL=text-embedding-3-large" >> .env
echo "OPENAI_CHAT_MODEL=gpt-4o" >> .env
echo "MILVUS_HOST=localhost" >> .env
echo "MILVUS_PORT=19530" >> .env

# CORS Configuration (đã được cấu hình sẵn cho dvc.ink)
# CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://dvc.ink,https://dvc.ink
```

### **Domain Configuration:**
- **localhost**: Development với các port options (3000, 8080, 80)
- **dvc.ink**: Production domain đã được cấu hình CORS
- **Custom domain**: Thêm vào `CORS_ORIGINS` trong `be/.env`

---

## 🌐 **Access Points**

### **Development (Local)**
| Service | URL | Description |
|---------|-----|-------------|
| 🎨 **Frontend** | http://localhost:8080 | Main application (khuyên dùng) |
| 🎨 **Frontend Alt** | http://localhost:3000 | Main application (classic) |
| ⚙️ **Backend API** | http://localhost:8001 | REST API |
| 📖 **API Docs** | http://localhost:8001/docs | Interactive API documentation |
| 🗄️ **MongoDB** | localhost:27017 | Database (admin/dvcai2025) |
| 🔍 **Milvus** | localhost:19530 | Vector Database |
| 🎛️ **Attu** | http://localhost:8080 | Milvus Admin UI (if port 8080 not used) |

### **Production (dvc.ink)**
| Service | URL | Description |
|---------|-----|-------------|
| 🎨 **Frontend** | http://dvc.ink | Main application |
| ⚙️ **Backend API** | http://dvc.ink:8001 | REST API |
| 📖 **API Docs** | http://dvc.ink:8001/docs | Interactive API documentation |

---

## 📚 **Documentation**

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- 🚀 **[Quick Start](docs/QUICK_START.md)** - Get started in 5 minutes
- 🐳 **[Deployment](docs/DEPLOYMENT.md)** - Complete deployment guide  
- 🛠️ **[Development](docs/DEVELOPMENT.md)** - Developer guide
- 🏗️ **[Architecture](docs/ARCHITECTURE.md)** - System architecture & AI
- 🗄️ **[Database](docs/DATABASE.md)** - MongoDB, Vector DB, Redis
- 🔧 **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Problem solving
- ⚙️ **[Backend API](be/README.md)** - Backend-specific documentation

**📖 Start here:** [`docs/README.md`](docs/README.md)

---

## 🔧 **Daily Commands**

### **Full Docker Stack**
```bash
# Start all services (after initial setup)
./deps/start.sh

# Stop all services  
docker compose down

# View logs
docker compose logs -f

# Restart specific service
docker compose restart backend

# Quick troubleshooting  
./deps/setup-docker.sh      # Fix Docker permissions
```

### **Frontend Development (npm)**
```bash
cd fe

# Option 1: Port 8080 (Khuyên dùng - không cần admin)
npm start                   # Sử dụng PORT=8080 từ .env
# hoặc
npm run start:8080

# Option 2: Port 80 (Cần quyền Administrator)  
npm run start:80

# Option 3: Port 3000 (Classic)
PORT=3000 npm start

# Option 4: Port tùy chỉnh
PORT=5000 npm start
```

### **Backend Development**
```bash
cd be

# Start backend only (cần Docker services chạy trước)
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Or with virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

## ⚙️ **System Requirements**

### **Minimum:**
- **OS**: Ubuntu 18.04+, Windows 10+, macOS 10.15+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 20GB free space
- **Docker**: 20.10+ with Docker Compose

### **Required Ports:**
- **Frontend Options:**
  - `8080` - Frontend React App (khuyên dùng - development)
  - `80` - Frontend React App (production hoặc với admin)
  - `3000` - Frontend React App (classic mode)
- **Backend & Services:**
  - `8001` - Backend FastAPI + AI Services
  - `27017` - MongoDB (Document metadata)
  - `6379` - Redis (Task queue)
  - `19530` - Milvus Vector DB (AI embeddings)
  
### **Port Conflicts:**
- Nếu port `8080` bị conflict với Attu (Milvus Admin), có thể:
  - Dùng `PORT=3000 npm start` cho frontend
  - Hoặc change Attu port trong docker-compose.yml

---

## 🏗️ **Project Structure**

```
📁 DVC.AI Project
├── 🎨 fe/                    # Frontend (React.js)
│   ├── components/          # UI Components với AI upload
│   └── services/            # API services
├── ⚙️  be/                   # Backend (FastAPI + AI Agent)
│   ├── app/utils/           # AI Document Processor
│   ├── app/workers/         # Celery AI tasks
│   └── app/services/        # Milvus, OpenAI services
├── 🛠️ deps/                 # Dependencies & Setup Scripts
├── 📚 docs/                 # Documentation
├── 📊 data/                 # Sample documents
└── 🐳 docker-compose.yml   # Docker orchestration
```

---

## 🔧 **Common Issues**

| Problem | Quick Solution |
|---------|---------------|
| Docker permission denied | `./deps/setup-docker.sh` |
| Port already in use | `netstat -tulpn \| grep :8080` (check port 8080/3000/80) |
| Port 80 permission denied | Chạy terminal với quyền Administrator hoặc dùng port 8080 |
| CORS error với domain mới | Thêm domain vào `CORS_ORIGINS` trong `be/.env` |
| Service not starting | `docker compose logs [service]` |
| OpenAI API issues | Check `OPENAI_API_KEY` in `.env` |
| File upload fails | Check Tesseract OCR installed |
| Milvus connection error | `docker ps \| grep milvus` |
| No content in vector DB | Check Celery worker logs |
| Frontend không kết nối backend | Kiểm tra `REACT_APP_API_URL` trong `fe/.env` |

**For detailed troubleshooting:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Create Pull Request

**Development setup:** [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

---

## 📄 **License**

This project is licensed under the MIT License.

## 🆘 **Support**

- 📖 **Documentation**: [docs/](docs/)
- 🔧 **Issues**: Create GitHub issue
- 💬 **Discussions**: GitHub Discussions

---

## 🌟 **Port Options Summary**

### **Development:**
```bash
# Khuyên dùng (không cần admin)
npm start                    # Port 8080 (từ .env)

# Các options khác  
npm run start:80            # Port 80 (cần admin)
PORT=3000 npm start         # Port 3000 (classic)
PORT=5000 npm start         # Port tùy chỉnh
```

### **Production:**
- **Domain**: `http://dvc.ink` (không cần port)
- **Backend**: `http://dvc.ink:8001`
- **Docker**: `docker-compose up -d` (frontend port 80:80)

---

**🎉 Ready to build intelligent virtual assistants? Start with [Quick Start Guide](docs/QUICK_START.md)! 🚀**