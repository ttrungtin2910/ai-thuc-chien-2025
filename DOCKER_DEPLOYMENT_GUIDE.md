# 🐳 DVC.AI Docker Deployment Guide

Hướng dẫn đầy đủ để deploy hệ thống **DVC.AI** bằng Docker và Docker Compose.

## 🚀 Tổng quan

Hệ thống DVC.AI bao gồm các services sau:
- **Frontend**: React app với Nginx (Port 3000)
- **Backend**: FastAPI Python (Port 8001)
- **MongoDB**: Database chính (Port 27017)
- **Redis**: Cache và message broker (Port 6379)
- **Milvus**: Vector database cho RAG (Port 19530)
- **Celery Worker**: Background tasks
- **Etcd & MinIO**: Support services cho Milvus

## 📋 Yêu cầu hệ thống

### Minimum Requirements
- **RAM**: 8GB (recommended 16GB)
- **Storage**: 20GB free space
- **CPU**: 4 cores (recommended)
- **OS**: Windows 10/11, macOS, Linux

### Software Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) >= 20.0
- [Docker Compose](https://docs.docker.com/compose/install/) >= 2.0
- Git

### Port Requirements
Đảm bảo các port sau không bị sử dụng:
- `3000` - Frontend
- `8001` - Backend API
- `27017` - MongoDB
- `6379` - Redis
- `19530` - Milvus
- `9091` - Milvus Web UI
- `2379` - Etcd
- `9000`, `9001` - MinIO

## ⚙️ Cấu hình

### 1. Environment Configuration

Tạo file `.env` từ template:

```bash
# Linux/macOS
cp .env.production .env

# Windows
copy .env.production .env
```

**Chỉnh sửa file `.env`:**

```bash
# BẮT BUỘC: Thiết lập OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# TÙY CHỌN: Google Cloud Storage (để trống nếu dùng local storage)
PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Security (thay đổi cho production)
SECRET_KEY=your-super-secret-key-here
```

### 2. Lấy OpenAI API Key

1. Truy cập [OpenAI Platform](https://platform.openai.com/api-keys)
2. Đăng nhập và tạo API key mới
3. Copy và paste vào file `.env`

## 🚀 Deployment

### Cách 1: Sử dụng Build Script (Recommended)

**Linux/macOS:**
```bash
chmod +x docker-build.sh
./docker-build.sh
```

**Windows:**
```cmd
docker-build.bat
```

### Cách 2: Manual Commands

```bash
# Build images
docker build -t dvc-ai-backend:latest ./be
docker build -t dvc-ai-frontend:latest ./fe

# Start services
docker-compose up -d --build

# Check status
docker-compose ps
```

## 🔧 Quản lý Services

### Kiểm tra status
```bash
# Xem tất cả services
docker-compose ps

# Xem logs
docker-compose logs -f

# Xem logs specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Điều khiển services
```bash
# Dừng tất cả services
docker-compose down

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Update và rebuild
docker-compose up -d --build
```

### Clean up
```bash
# Dừng và xóa containers + volumes
docker-compose down -v

# Xóa unused images
docker image prune -f

# Xóa tất cả (cẩn thận!)
docker system prune -a
```

## 🌐 Truy cập ứng dụng

Sau khi deploy thành công:

- **🖥️ Frontend**: http://localhost:3000
- **⚡ Backend API**: http://localhost:8001
- **📚 API Docs**: http://localhost:8001/docs
- **🔍 Interactive API**: http://localhost:8001/redoc

### Database Access
- **MongoDB**: `mongodb://admin:dvcai2025@localhost:27017/dvc_ai_db`
- **Redis**: `redis://localhost:6379/0`
- **Milvus**: `localhost:19530`

## 🛠️ Troubleshooting

### 1. Service không start được

**Kiểm tra logs:**
```bash
docker-compose logs [service-name]
```

**Common issues:**
- Port đã được sử dụng
- Thiếu RAM/disk space
- OPENAI_API_KEY chưa được set
- Docker daemon không chạy

### 2. Frontend không kết nối Backend

**Kiểm tra:**
```bash
# Test backend health
curl http://localhost:8001/health

# Check backend logs
docker-compose logs backend
```

### 3. Database connection errors

**MongoDB:**
```bash
# Check if MongoDB is running
docker-compose ps mongodb

# Connect to MongoDB
docker exec -it dvc-ai-mongodb mongosh -u admin -p dvcai2025
```

**Milvus:**
```bash
# Check Milvus health
curl http://localhost:9091/healthz

# Restart Milvus stack
docker-compose restart etcd minio milvus
```

### 4. Performance Issues

**Tăng memory limit:**
```yaml
# Trong docker-compose.yml, thêm:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### 5. SSL/HTTPS Issues

Cho production, sử dụng reverse proxy (Nginx/Traefik) với SSL:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:8001/api/;
    }
}
```

## 📊 Monitoring

### Health Checks
```bash
# Check all services health
curl http://localhost:8001/health
curl http://localhost:3000
curl http://localhost:9091/healthz

# MongoDB health
docker exec dvc-ai-mongodb mongosh --eval "db.adminCommand('ping')"

# Redis health
docker exec dvc-ai-redis redis-cli ping
```

### Resource Usage
```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Network usage
docker network ls
```

## 🔐 Security

### Production Security Checklist

- [ ] Thay đổi default passwords
- [ ] Set strong SECRET_KEY
- [ ] Sử dụng environment-specific configs
- [ ] Enable SSL/TLS
- [ ] Setup firewall rules
- [ ] Regular backup
- [ ] Monitor logs
- [ ] Update images regularly

### Backup Strategy

```bash
# Backup MongoDB
docker exec dvc-ai-mongodb mongodump --uri="mongodb://admin:dvcai2025@localhost:27017/dvc_ai_db" --out=/backup

# Backup uploaded files
docker cp dvc-ai-backend:/app/uploads ./backup-uploads

# Backup configurations
cp .env docker-compose.yml ./backup/
```

## 📱 Mobile/Remote Access

### LAN Access
Thay đổi `localhost` thành IP của máy chủ:
- Frontend: `http://YOUR_SERVER_IP:3000`
- Backend: `http://YOUR_SERVER_IP:8001`

### VPN/Remote Access
Sử dụng VPN hoặc SSH tunnel:
```bash
# SSH tunnel
ssh -L 3000:localhost:3000 -L 8001:localhost:8001 user@your-server
```

## 🎯 Performance Tuning

### Production Optimizations

**1. Database Indexing:**
MongoDB indexes được tự động tạo bởi init script.

**2. Redis Configuration:**
```yaml
redis:
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

**3. Nginx Caching:**
Frontend đã được tối ưu với Nginx caching trong `fe/nginx.conf`.

**4. Resource Limits:**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

## 📞 Support

Nếu gặp vấn đề:

1. **Kiểm tra logs**: `docker-compose logs`
2. **Restart services**: `docker-compose restart`
3. **Clean rebuild**: `docker-compose down && docker-compose up -d --build`
4. **GitHub Issues**: [Create issue](https://github.com/ttrungtin2910/ai-thuc-chien-2025/issues)

---

**© 2025 DVC.AI - Happy Coding! 🚀**
