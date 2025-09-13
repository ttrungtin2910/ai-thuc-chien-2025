# 🚀 Quick Start - DVC.AI

## ⚡ **1-Command Setup (Recommended)**

```bash
# Clone và khởi động toàn bộ hệ thống
git clone <repository-url>
cd dvc-ai-project
chmod +x docker-build.sh && ./docker-build.sh
```

**➡️ Truy cập:** http://localhost:3000

---

## 📋 **Prerequisites**

- **Docker & Docker Compose** (Docker Desktop >= 20.0)
- **OpenAI API Key** ([Get here](https://platform.openai.com/api-keys))
- **4GB RAM**, 20GB disk space

---

## ⚙️ **Configuration**

### 1. Setup API Key
```bash
# Tạo file .env với OpenAI API key
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

### 2. Optional: Custom Configuration
```bash
# Copy template (nếu cần custom)
cp be/env.example .env
# Edit với editor
nano .env
```

---

## 🐳 **Deployment Options**

### **Option 1: Full Auto (Ubuntu/Linux)**
```bash
# Setup Docker (first time)
./setup-docker.sh

# Deploy DVC.AI
./docker-build.sh

# Start services (subsequent times)
./start.sh
```

### **Option 2: Manual Steps**
```bash
# 1. Build images
docker build -t dvc-ai-backend ./be
docker build -t dvc-ai-frontend ./fe

# 2. Start services
docker compose up -d

# 3. Load documents (optional)
cd be
python scripts/load_documents_to_milvus.py
```

---

## 🌐 **Access Points**

| Service | URL | Credentials |
|---------|-----|-------------|
| 🎨 **Frontend** | http://localhost:3000 | - |
| ⚙️ **Backend API** | http://localhost:8001 | - |
| 📖 **API Docs** | http://localhost:8001/docs | - |
| 🗄️ **MongoDB** | localhost:27017 | admin/dvcai2025 |
| 🔴 **Redis** | localhost:6379 | - |
| 🔍 **Milvus** | localhost:19530 | - |

---

## 🎯 **Daily Commands**

```bash
# Start services
./start.sh

# Stop services  
docker compose down

# View logs
docker compose logs -f

# Restart specific service
docker compose restart backend
```

---

## 🔧 **Common Issues**

| Problem | Solution |
|---------|----------|
| Permission denied | `./setup-docker.sh` |
| Port in use | `sudo netstat -tulpn \| grep :3000` |
| Service not starting | `docker compose logs [service]` |

**Need detailed help?** ➡️ [Deployment Guide](DEPLOYMENT.md)