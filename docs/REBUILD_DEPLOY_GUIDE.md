# 🔄 REBUILD & DEPLOY GUIDE
## Hướng dẫn cập nhật và triển khai không mất dữ liệu

### 📋 **TÓM TẮT NHANH**
```bash
# Development với hot reload
dev-start.bat

# Update backend only
update-backend.bat

# Update frontend only  
update-frontend.bat

# Full rebuild (giữ nguyên database)
docker-build.bat
```

---

## 🔥 **1. DEVELOPMENT MODE (Hot Reload)**
**Dùng khi:** Code thường xuyên, cần xem thay đổi ngay lập tức

```bash
# Windows
dev-start.bat

# Manual
docker-compose -f docker-compose.dev.yml up --build
```

**✅ Ưu điểm:**
- Code changes tự động apply
- Không cần rebuild
- Nhanh nhất cho development

**❌ Nhược điểm:**  
- Chỉ dành cho development
- Có thể không stable như production build

---

## ⚡ **2. UPDATE TỪNG SERVICE (Recommended)**
### **Backend Update**
**Dùng khi:** Thay đổi API, business logic, dependencies Python

```bash
# Windows
update-backend.bat

# Manual  
docker-compose build backend
docker-compose up -d backend
docker-compose restart celery-worker
```

### **Frontend Update**  
**Dùng khi:** Thay đổi UI, components, styling

```bash
# Windows
update-frontend.bat

# Manual
docker-compose build frontend
docker-compose up -d frontend
```

---

## 🔄 **3. FULL REBUILD (Giữ nguyên Database)**
**Dùng khi:** 
- Thay đổi Dockerfile
- Thay đổi docker-compose.yml
- Thay đổi dependencies lớn
- Cần clean build hoàn toàn

```bash
# Windows
docker-build.bat

# Manual
docker-compose down
docker-compose up --build -d
```

**⚠️ LƯU Ý:** Lệnh này GIỮ NGUYÊN database volumes, không mất dữ liệu!

---

## 🗂️ **4. QUẢN LÝ DATABASE & VOLUMES**

### **Kiểm tra volumes hiện tại:**
```bash
docker volume ls
```

### **Backup database (khuyến nghị trước khi update lớn):**
```bash
# Backup MongoDB
docker exec dvc-ai-mongodb mongodump --out /data/backup/$(date +%Y%m%d)

# Backup Redis
docker exec dvc-ai-redis redis-cli BGSAVE
```

### **⚠️ Reset toàn bộ (MẤT DỮ LIỆU):**
```bash
# CẢNH BÁO: Lệnh này sẽ XÓA TẤT CẢ dữ liệu!
docker-compose down -v  # -v xóa volumes
docker system prune -a --volumes
```

---

## 🎯 **5. TROUBLESHOOTING**

### **Container unhealthy:**
```bash
# Xem logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart service
docker-compose restart backend
```

### **Port conflicts:**
```bash
# Kiểm tra port đang sử dụng
netstat -an | findstr :8001
netstat -an | findstr :3000

# Kill process nếu cần
taskkill /PID <process_id> /F
```

### **Out of disk space:**
```bash
# Cleanup Docker
docker system prune -a
docker image prune -a
docker volume prune  # CẢNH BÁO: Xóa volumes không dùng
```

---

## 📊 **6. MONITORING & HEALTH CHECK**

### **Kiểm tra trạng thái services:**
```bash
docker-compose ps
curl http://localhost:8001/health
curl http://localhost:3000
```

### **Xem resource usage:**
```bash
docker stats
```

### **Health check endpoints:**
- **Backend Health:** http://localhost:8001/health  
- **API Documentation:** http://localhost:8001/docs
- **Frontend:** http://localhost:3000
- **Milvus Admin:** http://localhost:9091
- **MongoDB:** localhost:27017 (admin/dvcai2025)
- **Redis:** localhost:6379

---

## 🔧 **7. DEVELOPMENT WORKFLOW**

### **Daily Development:**
1. `dev-start.bat` - Khởi động development mode
2. Code changes tự động reload
3. Test features
4. Commit changes

### **Before Major Updates:**
1. Backup database
2. Test in development mode first  
3. Use specific service updates (`update-backend.bat`)
4. Full rebuild if needed (`docker-build.bat`)

### **Production Deployment:**
1. Test thoroughly in development
2. Full rebuild (`docker-build.bat`)
3. Monitor health endpoints
4. Check logs for any issues

---

## ⚠️ **QUAN TRỌNG: KHÔNG MẤT DỮ LIỆU**

**Database volumes được persist qua các lần rebuild:**
- `mongodb_data:/data/db` 
- `redis_data:/data`
- `milvus_data:/var/lib/milvus`

**Chỉ MẤT dữ liệu khi:**
- Chạy `docker-compose down -v` (có flag -v)
- Chạy `docker volume prune` 
- Xóa volumes manually

**An toàn với:**
- `docker-compose down` (không có -v)
- `docker-compose up --build -d`
- `docker-build.bat`

---

## 🚀 **COMMANDS REFERENCE**

| Tác vụ | Command | Mất data? |
|--------|---------|-----------|
| Development | `dev-start.bat` | ❌ Không |
| Update Backend | `update-backend.bat` | ❌ Không |  
| Update Frontend | `update-frontend.bat` | ❌ Không |
| Full Rebuild | `docker-build.bat` | ❌ Không |
| Stop Services | `docker-compose down` | ❌ Không |
| **Reset ALL** | `docker-compose down -v` | ⚠️ **CÓ** |

---

**📝 Lưu ý:** Luôn kiểm tra `docker-compose ps` và logs sau mỗi lần update để đảm bảo services hoạt động bình thường!
