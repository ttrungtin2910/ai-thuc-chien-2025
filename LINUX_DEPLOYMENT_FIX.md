# 🐧 Linux/WSL Deployment Fix Guide

## 🚨 **Quick Fix cho lỗi hiện tại:**

### **1. Fix Line Endings (.env file)**
```bash
# Convert Windows line endings to Unix
tr -d '\r' < .env > .env.fixed && mv .env.fixed .env

# Hoặc dùng file đã fix sẵn
cp .env.unix .env
```

### **2. Fix Docker Permissions**
```bash
# Thêm user vào docker group
sudo usermod -aG docker $USER

# Restart session hoặc chạy:
newgrp docker

# Test Docker
docker --version
```

### **3. Fix Docker Compose**
```bash
# Kiểm tra version nào có sẵn
docker compose version  # v2
# hoặc
docker-compose --version  # v1

# Nếu không có, install:
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### **4. Chạy Deployment**
```bash
# Cấp quyền execute
chmod +x docker-build-fixed.sh
chmod +x fix-docker-permissions.sh

# Chạy script fixed
./docker-build-fixed.sh
```

---

## 🔧 **Hướng dẫn đầy đủ:**

### **Bước 1: Setup Docker (nếu chưa có)**
```bash
# Chạy script auto-fix
chmod +x fix-docker-permissions.sh
./fix-docker-permissions.sh

# Restart terminal sau khi script hoàn thành
```

### **Bước 2: Fix Environment File**
```bash
# Convert line endings
tr -d '\r' < .env > .env.tmp && mv .env.tmp .env

# Hoặc copy từ file Unix
cp .env.unix .env
```

### **Bước 3: Deploy với script fixed**
```bash
# Cấp quyền execute
chmod +x docker-build-fixed.sh

# Chạy deployment
./docker-build-fixed.sh
```

---

## 🐛 **Troubleshooting:**

### **Lỗi: "permission denied docker.sock"**
```bash
# Fix 1: Thêm user vào docker group
sudo usermod -aG docker $USER
newgrp docker

# Fix 2: Restart Docker service
sudo systemctl restart docker

# Fix 3: Chạy với sudo (không khuyến khích)
sudo ./docker-build-fixed.sh
```

### **Lỗi: "docker-compose command not found"**
```bash
# Install Docker Compose v1
sudo apt-get install docker-compose

# Hoặc sử dụng v2 syntax
docker compose up --build -d
```

### **Lỗi: "command not found" các lệnh khác**
```bash
# Install required tools
sudo apt-get update
sudo apt-get install curl wget git

# Cho WSL, đảm bảo có Windows Docker Desktop
```

---

## ✅ **Verification Steps:**

```bash
# 1. Check Docker
docker --version
docker ps

# 2. Check Docker Compose  
docker compose version
# hoặc
docker-compose --version

# 3. Check file permissions
ls -la docker-build-fixed.sh

# 4. Check .env file format
file .env  # should show "ASCII text" not "ASCII text, with CRLF"
```

---

## 🚀 **Commands Reference:**

| Issue | Solution |
|-------|----------|
| Windows line endings | `tr -d '\r' < .env > .env.tmp && mv .env.tmp .env` |
| Docker permissions | `sudo usermod -aG docker $USER && newgrp docker` |
| docker-compose missing | `sudo apt-get install docker-compose-plugin` |
| Script not executable | `chmod +x docker-build-fixed.sh` |
| Quick deploy | `./docker-build-fixed.sh` |

---

## 📱 **Platform-Specific Notes:**

### **Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
```

### **WSL (Windows Subsystem for Linux):**
- Ensure Docker Desktop for Windows is running
- Enable WSL integration in Docker Desktop settings

### **CentOS/RHEL:**
```bash
sudo yum install docker docker-compose
sudo systemctl start docker
```

**🎯 Sau khi fix xong, chạy `./docker-build-fixed.sh` để deploy thành công!**
