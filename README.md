# 🚀 DVC.AI - Virtual Assistant Platform

DVC.AI là một nền tảng trợ lý ảo thông minh được xây dựng với kiến trúc microservices, tích hợp các công nghệ AI tiên tiến để cung cấp dịch vụ hỗ trợ công dân trong các thủ tục hành chính.

## ✨ **Tính năng chính**

- 🤖 **AI Chatbot**: Tích hợp LangChain và OpenAI GPT-4
- 📚 **RAG System**: Retrieval-Augmented Generation cho tìm kiếm thông tin chính xác  
- 🗄️ **Vector Database**: Milvus để lưu trữ và tìm kiếm embeddings
- ⚡ **Real-time**: WebSocket communication
- 🏗️ **Microservices**: Kiến trúc tách biệt, dễ scale
- 🐳 **Docker**: Triển khai container hóa hoàn toàn

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

**➡️ Truy cập:** http://localhost:3000

### **Prerequisites:**
- Docker Desktop >= 20.0
- OpenAI API Key ([Get here](https://platform.openai.com/api-keys))
- 4GB RAM, 20GB disk space

### **Configuration:**
```bash
# Tạo .env với OpenAI API key
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

---

## 🌐 **Access Points**

| Service | URL | Description |
|---------|-----|-------------|
| 🎨 **Frontend** | http://localhost:3000 | Main application |
| ⚙️ **Backend API** | http://localhost:8001 | REST API |
| 📖 **API Docs** | http://localhost:8001/docs | Interactive API documentation |
| 🗄️ **MongoDB** | localhost:27017 | Database (admin/dvcai2025) |
| 🔍 **Milvus** | localhost:19530 | Vector Database |
| 🎛️ **Attu** | http://localhost:8080 | Milvus Admin UI |

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

```bash
# Start services (after initial setup)
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

---

## ⚙️ **System Requirements**

### **Minimum:**
- **OS**: Ubuntu 18.04+, Windows 10+, macOS 10.15+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 20GB free space
- **Docker**: 20.10+ with Docker Compose

### **Required Ports:**
- `3000` - Frontend
- `8001` - Backend API  
- `27017` - MongoDB
- `6379` - Redis
- `19530` - Milvus Vector DB

---

## 🏗️ **Project Structure**

```
📁 DVC.AI Project
├── 🎨 fe/                    # Frontend (React.js)
├── ⚙️  be/                   # Backend (FastAPI + AI Agent)
├── 🛠️ deps/                 # Dependencies & Setup Scripts
├── 📚 docs/                 # Documentation
├── 📊 data/                 # Sample data
└── 🐳 docker-compose.yml   # Docker orchestration
```

---

## 🔧 **Common Issues**

| Problem | Quick Solution |
|---------|---------------|
| Docker permission denied | `./deps/setup-docker.sh` |
| Port already in use | `sudo netstat -tulpn \| grep :3000` |
| Service not starting | `docker compose logs [service]` |
| OpenAI API issues | Check `OPENAI_API_KEY` in `.env` |

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

**🎉 Ready to build intelligent virtual assistants? Start with [Quick Start Guide](docs/QUICK_START.md)! 🚀**