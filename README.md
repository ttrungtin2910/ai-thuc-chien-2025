# 🌍 DVC.AI - Document Management & Virtual Assistant System

[![Version](https://img.shields.io/badge/version-3.3.0-orange.svg)](https://github.com/ttrungtin2910/ai-thuc-chien-2025)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com)

**DVC.AI** là hệ thống quản lý tài liệu thông minh tích hợp trợ lý ảo, được thiết kế đặc biệt để hỗ trợ công dân trong việc tra cứu và thực hiện các thủ tục hành chính tại Việt Nam.

## 🚀 Tính năng chính

- ✅ **Chat AI Real-time** - Trợ lý ảo với Markdown rendering và WebSocket
- ✅ **RAG System** - Retrieval-Augmented Generation với Milvus Vector DB
- ✅ **Document Management** - Upload, quản lý file PDF/DOCX với Google Cloud Storage
- ✅ **Microservice Architecture** - Kiến trúc modular, dễ mở rộng và bảo trì
- ✅ **Authentication** - Bảo mật JWT với session management
- ✅ **Real-time Upload** - Progress tracking với WebSocket và Celery
- ✅ **Modern UI/UX** - Theme Mệnh Thổ với font MaisonNeue

## 🏗️ Kiến trúc hệ thống

```
📁 DVC.AI System
├── 🖥️  Frontend (ReactJS)           # Modern UI với Markdown support
├── ⚡ Backend (FastAPI)             # Microservice architecture
├── 🧠 AI Services                   # OpenAI + Langraph + RAG
├── 🗄️  Databases                    # MongoDB + Milvus Vector DB
├── ☁️  Cloud Storage                # Google Cloud Storage
└── 🔄 Real-time Communication      # WebSocket + Socket.IO
```

## 📋 Cấu trúc dự án

```
📦 ai-thuc-chien-2025/
├── 📁 fe/                          # Frontend ReactJS
│   ├── 📁 src/components/           # Chat, Document Management
│   ├── 📁 public/fonts/             # MaisonNeue font family
│   └── 📄 package.json              # Dependencies
├── 📁 be/                           # Backend FastAPI
│   ├── 📁 app/                      # Main application
│   │   ├── 📁 api/                  # API routes (auth, chat, docs, rag)
│   │   ├── 📁 core/                 # Configuration & WebSocket
│   │   ├── 📁 services/             # AI, Database, Storage services
│   │   └── 📁 models/               # Data models
│   ├── 📁 scripts/                  # Utility scripts
│   └── 📄 requirements.txt          # Python dependencies
├── 📁 docs/                         # 📚 All Documentation
└── 📁 data/                         # Sample data & documents
```

## 🚀 Bắt đầu nhanh

### 1️⃣ Clone Repository
```bash
git clone https://github.com/ttrungtin2910/ai-thuc-chien-2025.git
cd ai-thuc-chien-2025
```

### 2️⃣ Setup Backend
```bash
cd be
conda create -n document-management-be python=3.9
conda activate document-management-be
pip install -r requirements.txt

# Copy and configure environment
cp env.example .env
# Edit .env file với OpenAI API key và các cấu hình khác
```

### 3️⃣ Setup Frontend
```bash
cd fe
npm install
npm start
```

### 4️⃣ Start Services
```bash
# Terminal 1: Backend
cd be && python -m app.main

# Terminal 2: Frontend  
cd fe && npm start

# Terminal 3: Vector Database (Optional)
cd be && ./start_milvus.sh
```

🌐 **Access:** Frontend tại http://localhost:3000, Backend API tại http://localhost:8001

## 📚 Tài liệu chi tiết

### 📖 Hướng dẫn chính
- **[📋 Complete Guide](docs/COMPLETE_GUIDE.md)** - Hướng dẫn toàn diện từ A-Z
- **[⚡ Quick Start](docs/QUICK_START.md)** - Khởi động nhanh trong 5 phút
- **[🏗️ Microservice Structure](docs/MICROSERVICE_STRUCTURE.md)** - Kiến trúc chi tiết

### 🤖 AI & Machine Learning
- **[🧠 Virtual Assistant Guide](docs/VIRTUAL_ASSISTANT_GUIDE.md)** - Trợ lý ảo với Langraph
- **[🔍 Vector Database Structure](docs/VECTOR_DB_STRUCTURE.md)** - Milvus và RAG system

### ⚙️ Cài đặt & Cấu hình
- **[🗄️ Milvus Setup Guide](docs/MILVUS_SETUP_GUIDE.md)** - Cài đặt Vector Database

## 🛠️ Công nghệ sử dụng

### Frontend
- **React 18** - Modern UI library
- **Ant Design** - UI components
- **ReactMarkdown** - Markdown rendering cho chat
- **Socket.IO Client** - Real-time communication

### Backend
- **FastAPI** - High-performance web framework
- **Langraph** - AI workflow orchestration
- **OpenAI API** - GPT-4o cho chat và text-embedding-3-large
- **Milvus** - Vector database cho RAG
- **MongoDB** - Document database
- **Socket.IO** - WebSocket real-time
- **Celery** - Background task processing

### Infrastructure
- **Google Cloud Storage** - File storage
- **Docker** - Containerization
- **Redis** - Caching và message broker
- **Conda** - Environment management

## 🔧 Environment Variables

Tạo file `.env` trong thư mục `be/`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Database URLs
MONGODB_URL=mongodb://localhost:27017
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Security
SECRET_KEY=your-secret-key-here

# Storage (Optional)
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:

1. **Fork** repository
2. **Tạo feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Tạo Pull Request**

## 📧 Liên hệ

- **GitHub**: [@ttrungtin2910](https://github.com/ttrungtin2910)
- **Email**: support@dvc.gov.vn
- **Issues**: [GitHub Issues](https://github.com/ttrungtin2910/ai-thuc-chien-2025/issues)

## 📄 License

Dự án được phân phối dưới giấy phép MIT. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

## 🎯 Roadmap

- [ ] **Multi-language Support** - Hỗ trợ tiếng Anh
- [ ] **Advanced Analytics** - Dashboard thống kê
- [ ] **Mobile App** - Ứng dụng di động
- [ ] **Voice Chat** - Chat bằng giọng nói
- [ ] **Document OCR** - Nhận dạng văn bản từ ảnh

---

**© 2025 DVC.AI - Hệ thống quản lý tài liệu và trợ lý ảo thông minh**

*Được phát triển với ❤️ tại Việt Nam*