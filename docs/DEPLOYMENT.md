# 🚀 DVC.AI Deployment Guide

## 📋 **System Requirements**

### **Minimum Requirements**
- **OS**: Ubuntu 18.04+, Windows 10+, macOS 10.15+
- **RAM**: 4GB (recommended 8GB+)
- **Storage**: 20GB free space
- **CPU**: 2 cores (recommended 4+)

### **Software Requirements**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) >= 20.0
- [Docker Compose](https://docs.docker.com/compose/install/) >= 1.29
- OpenAI API Key

### **Port Requirements**
Ensure these ports are available:
- `3000` - Frontend
- `8001` - Backend API  
- `27017` - MongoDB
- `6379` - Redis
- `19530` - Milvus Vector DB

---

## 🛠️ **Setup Docker (First Time)**

### **Ubuntu/Linux**
```bash
# Auto setup script
chmod +x setup-docker.sh
./setup-docker.sh

# Manual setup
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

### **Windows**
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install và restart
3. Enable WSL 2 backend

### **macOS**
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install và start Docker

---

## ⚙️ **Configuration**

### 1. **Environment Setup**

**Create .env file:**
```bash
# Linux/macOS
cp be/env.example .env

# Windows
copy be\env.example .env
```

**Required configuration:**
```env
# REQUIRED: OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Database
MONGODB_URL=mongodb://admin:dvcai2025@mongodb:27017/dvc_ai_db?authSource=admin
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Services
MILVUS_HOST=milvus
MILVUS_PORT=19530

# Optional: Google Cloud Storage
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 2. **Get OpenAI API Key**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy to `.env` file

---

## 🚀 **Deployment Methods**

### **Method 1: Automated Script (Recommended)**

**Ubuntu/Linux:**
```bash
chmod +x docker-build.sh
./docker-build.sh
```

**Windows:**
```cmd
docker-build.bat
```

### **Method 2: Manual Deployment**

**Step 1: Build Images**
```bash
# Build backend
docker build -t dvc-ai-backend:latest ./be

# Build frontend  
docker build -t dvc-ai-frontend:latest ./fe
```

**Step 2: Start Services**
```bash
# Start all services
docker compose up -d --build

# Check status
docker compose ps
```

**Step 3: Load Documents (Optional)**
```bash
cd be
python scripts/load_documents_to_milvus.py
```

---

## 📊 **Service Health Check**

### **Verify Deployment**
```bash
# Check all services
docker compose ps

# Check logs
docker compose logs -f

# Test endpoints
curl http://localhost:8001/health
curl http://localhost:3000
```

### **Expected Services**
| Service | Container | Status | Port |
|---------|-----------|--------|------|
| Frontend | dvc-ai-frontend | Running | 3000 |
| Backend | dvc-ai-backend | Running | 8001 |
| MongoDB | mongo | Running | 27017 |
| Redis | redis | Running | 6379 |
| Milvus | milvus-standalone | Running | 19530 |
| MinIO | minio | Running | 9000 |
| Etcd | etcd | Running | 2379 |

---

## 🔄 **Daily Operations**

### **Start/Stop Services**
```bash
# Start (after initial deployment)
./start.sh
# or
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

### **View Logs**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f milvus-standalone
```

### **Update Deployment**
```bash
# Rebuild and restart
docker compose up -d --build

# Force rebuild
docker compose build --no-cache
docker compose up -d
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Docker Permission Denied**
```bash
# Solution 1: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Solution 2: Use setup script
./setup-docker.sh
```

#### **Port Already in Use**
```bash
# Find process using port
sudo netstat -tulpn | grep :3000
sudo lsof -i :8001

# Kill process
sudo kill -9 <PID>
```

#### **Service Not Starting**
```bash
# Check logs
docker compose logs [service-name]

# Check resources
docker system df
docker system prune -f

# Restart Docker
sudo systemctl restart docker
```

#### **Out of Disk Space**
```bash
# Clean Docker
docker system prune -a
docker volume prune

# Check disk usage
df -h
```

#### **Environment Issues**
```bash
# Fix line endings (Windows)
tr -d '\r' < .env > .env.tmp && mv .env.tmp .env

# Check environment
docker compose config
```

### **Service-Specific Issues**

#### **MongoDB Connection Issues**
```bash
# Check MongoDB logs
docker compose logs mongo

# Connect to MongoDB
docker compose exec mongo mongosh -u admin -p dvcai2025
```

#### **Milvus Issues**
```bash
# Check Milvus logs
docker compose logs milvus-standalone

# Check dependencies
docker compose logs etcd
docker compose logs minio
```

#### **Frontend Not Loading**
```bash
# Check nginx logs
docker compose logs frontend

# Rebuild frontend
docker compose build frontend --no-cache
```

---

## 📈 **Performance Optimization**

### **Resource Allocation**
```yaml
# docker-compose.yml adjustments
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### **Database Optimization**
```bash
# MongoDB indexing
docker compose exec mongo mongosh --eval "db.documents.createIndex({title: 'text', content: 'text'})"

# Milvus collection optimization
python scripts/optimize_milvus_collection.py
```

---

## 🎯 **Production Considerations**

### **Security**
- Change default passwords in `docker-compose.yml`
- Use strong `SECRET_KEY` và `JWT_SECRET_KEY`
- Enable HTTPS with reverse proxy
- Restrict network access

### **Backup**
```bash
# MongoDB backup
docker compose exec mongo mongodump --uri="mongodb://admin:dvcai2025@localhost:27017/dvc_ai_db?authSource=admin"

# Milvus backup
python scripts/backup_milvus_collection.py
```

### **Monitoring**
- Setup log aggregation
- Monitor resource usage
- Health check endpoints
- Error tracking

---

**🎉 Deployment Complete!** ➡️ Access your DVC.AI at http://localhost:3000
