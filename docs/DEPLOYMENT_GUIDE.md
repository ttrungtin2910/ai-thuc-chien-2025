# 🚀 DVC.AI Ubuntu/Linux Deployment Guide

## 📋 **Quick Start**

```bash
# 1. Setup Docker (first time only)
chmod +x setup-docker.sh && ./setup-docker.sh

# 2. Deploy DVC.AI
chmod +x docker-build.sh && ./docker-build.sh

# 3. Start services (after first deployment)
./start.sh
```

---

## 🛠️ **Prerequisites**

### **System Requirements:**
- Ubuntu 18.04+ / Debian 10+ / CentOS 7+
- 4GB RAM minimum (8GB recommended)
- 20GB free disk space
- Internet connection

### **Required Software:**
- Docker Engine 20.10+
- Docker Compose v1.29+ or v2.x

---

## 📦 **Installation Steps**

### **Step 1: Clone Repository**
```bash
git clone <your-repo-url>
cd dvc-ai-project
```

### **Step 2: Setup Docker (First Time)**
```bash
chmod +x setup-docker.sh
./setup-docker.sh

# Restart terminal or run:
newgrp docker
```

### **Step 3: Configure Environment**
```bash
# Copy template (if exists)
cp be/env.example .env

# Edit configuration
nano .env
```

**Required .env variables:**
```env
# OpenAI Configuration (required)
OPENAI_API_KEY=your-openai-api-key-here

# Optional configurations
SECRET_KEY=your-secret-key
MONGODB_URL=mongodb://admin:dvcai2025@mongodb:27017/dvc_ai_db?authSource=admin
```

### **Step 4: Deploy**
```bash
chmod +x docker-build.sh
./docker-build.sh
```

---

## 🔧 **Scripts Overview**

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `setup-docker.sh` | Setup Docker & permissions | First time setup |
| `docker-build.sh` | Full build & deploy | Initial deployment, major updates |
| `start.sh` | Start existing containers | Daily start |
| `quick-fix.sh` | Fix common issues | Troubleshooting |

---

## 🐛 **Troubleshooting**

### **Docker Permission Denied**
```bash
# Fix permissions
sudo usermod -aG docker $USER
newgrp docker

# Or run setup
./setup-docker.sh
```

### **Port Already in Use**
```bash
# Check what's using ports
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8001

# Kill processes
sudo kill -9 <PID>
```

### **Service Not Starting**
```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Restart specific service
docker compose restart backend
```

### **Out of Disk Space**
```bash
# Clean up Docker
docker system prune -a
docker volume prune  # WARNING: removes unused volumes
```

### **Line Ending Issues**
```bash
# Fix automatically
./quick-fix.sh

# Or manually
tr -d '\r' < .env > .env.tmp && mv .env.tmp .env
```

---

## 📊 **Service Health Check**

### **Check All Services:**
```bash
docker compose ps
```

### **Test Endpoints:**
```bash
# Backend health
curl http://localhost:8001/health

# Frontend
curl -I http://localhost:3000

# API documentation
curl -I http://localhost:8001/docs
```

### **Expected Response:**
```json
{
  "status": "healthy",
  "version": "3.1.0"
}
```

---

## 🔄 **Daily Operations**

### **Start Services:**
```bash
./start.sh
```

### **Stop Services:**
```bash
docker compose down
```

### **Restart Services:**
```bash
docker compose restart
```

### **View Logs:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### **Update Application:**
```bash
# Pull latest code
git pull origin main

# Rebuild and deploy
./docker-build.sh
```

---

## 🌐 **Access Points**

After successful deployment:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **MongoDB**: localhost:27017 (admin/dvcai2025)
- **Redis**: localhost:6379
- **Milvus**: localhost:19530

---

## 📁 **Project Structure**

```
dvc-ai-project/
├── be/                     # Backend (FastAPI)
├── fe/                     # Frontend (React)
├── docs/                   # Documentation
├── docker-compose.yml      # Main deployment config
├── docker-build.sh         # Main deployment script
├── setup-docker.sh         # Docker setup script
├── start.sh               # Start existing containers
├── quick-fix.sh           # Fix common issues
└── .env                   # Environment configuration
```

---

## 🔒 **Security Notes**

- **Never commit .env files** to git
- **Change default passwords** in production
- **Use HTTPS** in production environments
- **Regularly update** Docker images
- **Monitor logs** for suspicious activity

---

## 🆘 **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| Permission denied | `./setup-docker.sh` |
| Port in use | Check and kill processes |
| Build fails | Check logs, fix dependencies |
| Service unhealthy | Wait 2-3 minutes, check logs |
| Memory issues | Increase system RAM |
| Disk full | `docker system prune -a` |

---

## 📞 **Support**

If you encounter issues:

1. **Check logs**: `docker compose logs`
2. **Run quick fix**: `./quick-fix.sh`
3. **Check this guide**: Review troubleshooting section
4. **Clean start**: `docker compose down && ./docker-build.sh`

---

**🎯 Happy deployment with DVC.AI on Ubuntu/Linux! 🚀**
