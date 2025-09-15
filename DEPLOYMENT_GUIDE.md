# 🚀 Production Deployment Guide

## Issues Fixed
- ✅ Frontend proxy error (localhost:8001 → production IP)
- ✅ WebSocket connection error in production  
- ✅ Environment-specific configuration
- ✅ CORS configuration for dvc.ink domain
- ✅ Multiple port options (80, 8080, 3000)

## 🎯 Quick Commands Summary

### Production Deployment (Port 80 - khuyên dùng):
```bash
npm run build:prod
sudo pm2 serve build 80 --name "frontend" --spa
```
**Access:** `http://dvc.ink` (no port needed)

### Alternative (Port 8080 - no sudo required):
```bash
npm run build:prod  
pm2 serve build 8080 --name "frontend" --spa
```
**Access:** `http://dvc.ink:8080`

### Classic (Port 3000):
```bash
npm run build:prod
pm2 serve build 3000 --name "frontend" --spa
```
**Access:** `http://dvc.ink:3000`

## 🔧 Frontend Configuration

### 1. Update `.env.production` file
Create `fe/.env.production` with your internal server IP:
```env
REACT_APP_API_URL=http://10.128.0.4:8001
REACT_APP_WS_URL=http://10.128.0.4:8001
```

This uses the internal IP address for secure communication within the network.

### 2. Build for Production
```bash
cd fe
npm run build
```

## 🐳 Backend Configuration

### 1. Update Backend .env
Ensure `be/.env` has correct configuration:
```env
# CORS Configuration for domain dvc.ink (already configured)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://dvc.ink,https://dvc.ink,http://dvc.ink:80,https://dvc.ink:443,http://dvc.ink:8001

# WebSocket Configuration
WEBSOCKET_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://dvc.ink,https://dvc.ink,http://dvc.ink:80,https://dvc.ink:443

# Add your internal IP if needed
# CORS_ORIGINS=...,http://10.128.0.4:3000,http://10.128.0.4:8080
```

### 2. Start Backend Services
```bash
cd be

# Start Docker services (MongoDB, Redis, etc.)
python scripts/setup.py start

# Start backend API
python main.py
```

## 🌐 Production Setup Options

### Option 1: PM2 (Recommended)
```bash
# Install PM2
npm install -g pm2

# Start backend with PM2
cd be
pm2 start main.py --name "dvc-ai-backend" --interpreter python3

# Start frontend with PM2 (choose one option)
cd fe

# Option 1: Port 80 (Production - cần sudo)
sudo pm2 serve build 80 --name "dvc-ai-frontend" --spa

# Option 2: Port 8080 (Khuyên dùng - không cần sudo) 
pm2 serve build 8080 --name "dvc-ai-frontend" --spa

# Option 3: Port 3000 (Classic)
pm2 serve build 3000 --name "dvc-ai-frontend" --spa

# Save PM2 configuration
pm2 save
pm2 startup
```

### Option 2: Direct Process
```bash
# Terminal 1: Backend
cd be
python main.py

# Terminal 2: Frontend (serve build)
cd fe
npx serve -s build -p 3000
```

### Option 3: Docker Production
Update docker-compose.yml for production environment.

## 🔒 Security Considerations

1. **Firewall Configuration**:
   ```bash
   # Allow necessary ports - choose based on your frontend port option
   sudo ufw allow 80/tcp    # Frontend (Option 1)
   sudo ufw allow 8080/tcp  # Frontend (Option 2) 
   sudo ufw allow 3000/tcp  # Frontend (Option 3)
   sudo ufw allow 8001/tcp  # Backend API (always needed)
   ```

2. **Environment Variables**:
   - Never commit production `.env` files
   - Use strong passwords for MongoDB/Redis
   - Change default JWT secrets

3. **SSL/HTTPS** (Optional but recommended):
   - Use reverse proxy (Nginx/Apache)
   - Configure SSL certificates
   - Update URLs to HTTPS

## 📋 Troubleshooting

### Frontend Proxy Errors:
```bash
# Check if backend is running
curl http://10.128.0.4:8001/api/auth/me

# Check frontend environment
cat fe/.env.production
```

### WebSocket Connection Issues:
```bash
# Check WebSocket connection
curl -I http://10.128.0.4:8001/socket.io/

# Check browser console for WebSocket errors
```

### Port Already in Use:
```bash
# Kill process using port
sudo lsof -ti:8001 | xargs kill -9
sudo lsof -ti:80 | xargs kill -9    # If using port 80
sudo lsof -ti:8080 | xargs kill -9  # If using port 8080
sudo lsof -ti:3000 | xargs kill -9  # If using port 3000
```

## ✅ Health Check

After deployment, verify:

### Frontend Accessibility (choose based on your port option):
- **Option 1 (Port 80)**: `http://dvc.ink` hoặc `http://10.128.0.4`
- **Option 2 (Port 8080)**: `http://dvc.ink:8080` hoặc `http://10.128.0.4:8080`  
- **Option 3 (Port 3000)**: `http://dvc.ink:3000` hoặc `http://10.128.0.4:3000`

### Backend & Features:
1. ✅ Backend API: `http://dvc.ink:8001/docs` hoặc `http://10.128.0.4:8001/docs`
2. ✅ WebSocket connection working
3. ✅ File upload functionality
4. ✅ Chat functionality
5. ✅ CORS working with dvc.ink domain

## 📝 Environment Template

Production environment configuration for `fe/.env.production`:

### Option A: Domain-based (Khuyên dùng - Đã cập nhật)
```env
# Domain-based configuration to avoid CORS issues
REACT_APP_API_URL=http://dvc.ink:8001
REACT_APP_WS_URL=http://dvc.ink:8001

# Production optimizations
GENERATE_SOURCEMAP=false
REACT_APP_ENV=production
```

### Option B: IP-based (Legacy)
```env
# IP-based configuration (can cause CORS issues)
REACT_APP_API_URL=http://35.232.207.211:8001
REACT_APP_WS_URL=http://35.232.207.211:8001

# Production optimizations
GENERATE_SOURCEMAP=false
REACT_APP_ENV=production
```

### ⚠️ **CORS Issue Fix**
Nếu gặp CORS error khi call từ `http://dvc.ink` sang IP, đã fix bằng cách:
1. ✅ Đổi `.env.production` từ IP sang domain
2. ✅ Thêm IP vào CORS origins trong backend
3. ✅ Rebuild frontend với config mới
