# 🚀 Production Deployment Guide

## Issues Fixed
- ✅ Frontend proxy error (localhost:8001 → production IP)
- ✅ WebSocket connection error in production  
- ✅ Environment-specific configuration

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
# Backend should accept connections from internal IP
WEBSOCKET_CORS_ORIGINS=http://10.128.0.4:3000,http://localhost:3000,http://127.0.0.1:3000
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

# Start frontend with PM2 
cd fe
pm2 serve build 3000 --name "dvc-ai-frontend"

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
   # Allow necessary ports
   sudo ufw allow 3000/tcp  # Frontend
   sudo ufw allow 8001/tcp  # Backend API
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
sudo lsof -ti:3000 | xargs kill -9
```

## ✅ Health Check

After deployment, verify:
1. ✅ Frontend accessible: `http://10.128.0.4:3000`
2. ✅ Backend API: `http://10.128.0.4:8001/docs`
3. ✅ WebSocket connection working
4. ✅ File upload functionality
5. ✅ Chat functionality

## 📝 Environment Template

Production environment configuration for `fe/.env.production`:
```env
# Internal IP for production deployment
REACT_APP_API_URL=http://10.128.0.4:8001
REACT_APP_WS_URL=http://10.128.0.4:8001

# Production optimizations
GENERATE_SOURCEMAP=false
REACT_APP_ENV=production
```
