# DVC.AI - Virtual Assistant Platform

DVC.AI là một nền tảng trợ lý ảo thông minh được xây dựng với kiến trúc microservices, tích hợp các công nghệ AI tiên tiến để cung cấp dịch vụ hỗ trợ công dân trong các thủ tục hành chính.

## 🚀 Tính năng chính

- **Chatbot thông minh**: Tích hợp LangChain và OpenAI để trả lời câu hỏi về thủ tục hành chính
- **RAG System**: Hệ thống Retrieval-Augmented Generation để tìm kiếm thông tin chính xác
- **Vector Database**: Sử dụng Milvus để lưu trữ và tìm kiếm vector embeddings
- **WebSocket**: Giao tiếp real-time với người dùng
- **Microservices**: Kiến trúc tách biệt giữa frontend, backend, và các dịch vụ hỗ trợ
- **Docker**: Triển khai dễ dàng với containerization

## 📁 Cấu trúc dự án

```
├── fe/                 # Frontend (React.js)
├── be/                 # Backend (FastAPI + Python)
├── docs/               # Tài liệu hướng dẫn
├── data/               # Dữ liệu thủ tục công dân
└── docker-compose.yml  # Docker orchestration
```

## 🛠️ Hướng dẫn cài đặt và triển khai

### 📚 Tài liệu hướng dẫn

Tất cả các hướng dẫn chi tiết đã được tổ chức trong thư mục `docs/`:

#### 🚀 Bắt đầu nhanh
- **[Quick Start Guide](docs/QUICK_START.md)** - Hướng dẫn cài đặt và chạy nhanh dự án

#### 🏗️ Triển khai và Docker
- **[Docker Deployment Guide](docs/DOCKER_DEPLOYMENT_GUIDE.md)** - Hướng dẫn triển khai với Docker
- **[Rebuild Deploy Guide](docs/REBUILD_DEPLOY_GUIDE.md)** - Hướng dẫn rebuild và deploy lại

#### 🏛️ Kiến trúc và cấu trúc
- **[Complete Guide](docs/COMPLETE_GUIDE.md)** - Hướng dẫn tổng quan và đầy đủ
- **[Microservice Structure](docs/MICROSERVICE_STRUCTURE.md)** - Kiến trúc microservices
- **[Vector Database Structure](docs/VECTOR_DB_STRUCTURE.md)** - Cấu trúc cơ sở dữ liệu vector

#### 🤖 AI và Virtual Assistant
- **[Virtual Assistant Guide](docs/VIRTUAL_ASSISTANT_GUIDE.md)** - Hướng dẫn về trợ lý ảo
- **[Enhanced Agent Guide](docs/ENHANCED_AGENT_GUIDE.md)** - Hướng dẫn về enhanced agent
- **[Milvus Setup Guide](docs/MILVUS_SETUP_GUIDE.md)** - Cài đặt và cấu hình Milvus

### ⚡ Khởi động nhanh

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd 02-AI-ThucChien
   ```

2. **Chạy với Docker (Khuyến nghị):**
   ```bash
   # Windows
   docker-build.bat
   
   # Linux/Mac
   ./docker-build.sh
   ```

3. **Truy cập ứng dụng:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Milvus Dashboard: http://localhost:3001

## 🔧 Công nghệ sử dụng

### Backend
- **FastAPI** - Web framework
- **LangChain** - LLM framework
- **OpenAI** - AI API
- **Milvus** - Vector database
- **MongoDB** - Document database
- **Redis** - Cache và message broker
- **Celery** - Background tasks

### Frontend
- **React.js** - UI framework
- **WebSocket** - Real-time communication
- **MaisonNeue** - Font chính (theo brand guidelines)

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Google Cloud Storage** - File storage

## 📊 Dữ liệu

Dự án sử dụng dữ liệu thủ tục công dân từ Văn phòng Đăng ký Đất đai tỉnh Vĩnh Long, được xử lý và vector hóa để phục vụ tìm kiếm thông tin.

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 License

Dự án này được phát triển cho mục đích nghiên cứu và học tập.

## 📞 Liên hệ

- **Phát triển bởi**: DVC.AI Team
- **Màu sắc chủ đạo**: Orange-brown (theo brand guidelines)
- **Font chính**: MaisonNeue

---

> 💡 **Lưu ý**: Để có hướng dẫn chi tiết về từng thành phần, vui lòng tham khảo các file trong thư mục `docs/`.