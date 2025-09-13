# 🚀 DVC.AI - Virtual Assistant Platform

DVC.AI là một nền tảng trợ lý ảo thông minh được xây dựng với kiến trúc microservices, tích hợp các công nghệ AI tiên tiến để cung cấp dịch vụ hỗ trợ công dân trong các thủ tục hành chính.

## ✨ **Tính năng chính**

- 🤖 **AI Chatbot**: Tích hợp LangChain và OpenAI GPT-4
- 📚 **RAG System**: Retrieval-Augmented Generation cho tìm kiếm thông tin chính xác  
- 🗄️ **Vector Database**: Milvus để lưu trữ và tìm kiếm embeddings
- ⚡ **Real-time**: WebSocket communication
- 🏗️ **Microservices**: Kiến trúc tách biệt, dễ scale
- 🐳 **Docker**: Triển khai container hóa hoàn toàn

## 🏁 **Khởi động nhanh (Ubuntu/Linux)**

```bash
# 1. Clone repository
git clone <repository-url>
cd dvc-ai-project

# 2. Setup Docker (chỉ lần đầu)
chmod +x setup-docker.sh && ./setup-docker.sh

# 3. Deploy DVC.AI  
chmod +x docker-build.sh && ./docker-build.sh

# 4. Truy cập ứng dụng
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

## 📁 **Cấu trúc dự án**

```
dvc-ai-project/
├── 🎨 fe/                     # Frontend (React.js)
├── ⚙️  be/                     # Backend (FastAPI + Python)  
├── 📚 docs/                   # Documentation
├── 📊 data/                   # Dữ liệu thủ tục công dân
├── 🐳 docker-compose.yml      # Docker orchestration
├── 🚀 docker-build.sh         # Deployment script
├── 🛠️ setup-docker.sh         # Docker setup
├── ▶️  start.sh               # Start services
└── 🔧 quick-fix.sh           # Fix common issues
```

## 🛠️ **Scripts & Commands**

| Script | Mục đích | Khi nào sử dụng |
|--------|----------|------------------|
| `setup-docker.sh` | Cài đặt Docker & permissions | Lần đầu setup |
| `docker-build.sh` | Build & deploy toàn bộ | Deploy chính, cập nhật lớn |
| `start.sh` | Start containers có sẵn | Khởi động hàng ngày |
| `quick-fix.sh` | Fix lỗi thường gặp | Troubleshooting |

### **Thao tác hàng ngày:**

```bash
# Khởi động services
./start.sh

# Dừng services  
docker compose down

# Xem logs
docker compose logs -f

# Restart service cụ thể
docker compose restart backend
```

## 🌐 **Truy cập ứng dụng**

Sau khi deploy thành công:

- **🎨 Frontend**: http://localhost:3000
- **⚙️ Backend API**: http://localhost:8001  
- **📖 API Documentation**: http://localhost:8001/docs
- **🗄️ MongoDB**: localhost:27017 (admin/dvcai2025)
- **🔴 Redis**: localhost:6379
- **🔍 Milvus**: localhost:19530

## 📚 **Tài liệu chi tiết**

### **📋 Deployment:**
- **[🚀 Deployment Guide](DEPLOYMENT_GUIDE.md)** - Hướng dẫn deployment Ubuntu/Linux đầy đủ
- **[🐳 Docker Setup](setup-docker.sh)** - Script setup Docker tự động

### **🏗️ Architecture:**
- **[📐 Complete Guide](docs/COMPLETE_GUIDE.md)** - Hướng dẫn tổng quan
- **[🏛️ Microservice Structure](docs/MICROSERVICE_STRUCTURE.md)** - Kiến trúc microservices
- **[🗄️ Vector Database](docs/VECTOR_DB_STRUCTURE.md)** - Cấu trúc Milvus

### **🤖 AI Features:**
- **[🧠 Virtual Assistant](docs/VIRTUAL_ASSISTANT_GUIDE.md)** - Hướng dẫn AI assistant
- **[⚡ Enhanced Agent](docs/ENHANCED_AGENT_GUIDE.md)** - Enhanced agent features

## ⚙️ **Cấu hình**

### **Environment Variables (.env):**

```env
# OpenAI (Required)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Security
SECRET_KEY=your-secret-key-here

# Database (Auto-configured for Docker)
MONGODB_URL=mongodb://admin:dvcai2025@mongodb:27017/dvc_ai_db?authSource=admin
REDIS_URL=redis://redis:6379/0
MILVUS_HOST=milvus
MILVUS_PORT=19530
```

## 🔧 **Yêu cầu hệ thống**

- **OS**: Ubuntu 18.04+, Debian 10+, CentOS 7+
- **RAM**: 4GB tối thiểu (8GB khuyến nghị)
- **Disk**: 20GB free space
- **Docker**: 20.10+
- **Docker Compose**: v1.29+ hoặc v2.x

## 🐛 **Troubleshooting**

### **Lỗi phổ biến:**

```bash
# Docker permission denied
./setup-docker.sh

# Port đã được sử dụng
sudo netstat -tulpn | grep :3000
sudo kill -9 <PID>

# Service không start
docker compose logs backend

# Fix line endings 
./quick-fix.sh

# Clean Docker 
docker system prune -a
```

## 🤝 **Đóng góp**

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Tạo Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Hỗ trợ**

- 📖 **Documentation**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- 🔧 **Issues**: Create GitHub issue
- 💬 **Discussions**: GitHub Discussions

---

**🎯 Phát triển bởi DVC.AI Team - Trợ lý ảo thông minh cho dịch vụ công! 🚀**