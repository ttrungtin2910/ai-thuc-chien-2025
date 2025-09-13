# 🔧 Troubleshooting Guide - DVC.AI

## 🚨 **Common Issues & Solutions**

### **Docker Issues**

#### **🔴 Docker Permission Denied**
```bash
# Symptoms
docker: permission denied while trying to connect to the Docker daemon socket

# Solutions
# 1. Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# 2. Use setup script
./setup-docker.sh

# 3. Restart Docker service
sudo systemctl restart docker

# 4. Restart your terminal/computer
```

#### **🔴 Port Already in Use**
```bash
# Symptoms
Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use

# Find process using port
sudo netstat -tulpn | grep :3000
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>

# Alternative: Change port in docker-compose.yml
ports:
  - "3001:3000"  # Use port 3001 instead
```

#### **🔴 Docker Compose Not Found**
```bash
# Symptoms
docker-compose: command not found

# Solutions
# 1. Install Docker Compose plugin (Ubuntu)
sudo apt-get install docker-compose-plugin

# 2. Use docker compose (v2)
docker compose up -d

# 3. Install standalone (if needed)
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### **🔴 Container Keeps Restarting**
```bash
# Check logs
docker-compose logs -f [service-name]

# Common causes:
# 1. Missing environment variables
# 2. Database connection issues
# 3. Port conflicts
# 4. Memory/resource limits

# Fix: Check .env file
cp be/env.example .env
# Add required variables

# Fix: Increase memory limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 2G
```

---

### **Database Issues**

#### **🔴 MongoDB Connection Failed**
```bash
# Symptoms
pymongo.errors.ServerSelectionTimeoutError: [Errno 111] Connection refused

# Check MongoDB status
docker-compose logs mongo

# Solutions
# 1. Restart MongoDB
docker-compose restart mongo

# 2. Check MongoDB credentials in .env
MONGODB_URL=mongodb://admin:dvcai2025@mongodb:27017/dvc_ai_db?authSource=admin

# 3. Reset MongoDB data (⚠️ will lose data)
docker-compose down
docker volume rm $(docker volume ls -q | grep mongo)
docker-compose up -d mongo

# 4. Connect manually to test
docker-compose exec mongo mongosh -u admin -p dvcai2025
```

#### **🔴 Milvus Connection Issues**
```bash
# Symptoms
Cannot connect to Milvus server at localhost:19530

# Check Milvus status
docker-compose logs milvus-standalone
docker-compose logs etcd
docker-compose logs minio

# Solutions
# 1. Restart Milvus stack
docker-compose restart etcd minio milvus-standalone

# 2. Check dependencies
# Milvus requires etcd and minio to be healthy first

# 3. Increase startup time
# Wait 60 seconds after starting before testing

# 4. Reset Milvus data (⚠️ will lose vectors)
docker-compose down
docker volume rm $(docker volume ls -q | grep milvus)
docker-compose up -d
```

#### **🔴 Redis Connection Issues**
```bash
# Symptoms
redis.exceptions.ConnectionError: Error 111 connecting to redis:6379

# Check Redis status
docker-compose logs redis

# Solutions
# 1. Restart Redis
docker-compose restart redis

# 2. Check Redis URL in .env
REDIS_URL=redis://redis:6379/0

# 3. Test connection
docker-compose exec redis redis-cli ping
# Should respond: PONG
```

---

### **API Issues**

#### **🔴 Backend API Not Responding**
```bash
# Symptoms
curl: (7) Failed to connect to localhost port 8001: Connection refused

# Check backend status
docker-compose logs backend

# Solutions
# 1. Check if container is running
docker-compose ps

# 2. Restart backend
docker-compose restart backend

# 3. Check backend logs for errors
docker-compose logs -f backend

# 4. Test health endpoint
curl http://localhost:8001/health

# 5. Check .env configuration
# Ensure all required variables are set
```

#### **🔴 OpenAI API Key Issues**
```bash
# Symptoms
openai.error.AuthenticationError: Incorrect API key provided

# Solutions
# 1. Check API key in .env
OPENAI_API_KEY=sk-your-actual-key-here

# 2. Verify key is valid
# Visit: https://platform.openai.com/api-keys

# 3. Check key format
# Should start with "sk-" and be 51 characters long

# 4. Restart backend after changing
docker-compose restart backend
```

#### **🔴 CORS Issues**
```bash
# Symptoms
Access to fetch at 'http://localhost:8001/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy

# Solutions
# 1. Check CORS configuration in backend
# app/main.py should have:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. For production, update allowed origins
allow_origins=["https://yourdomain.com"]
```

---

### **Frontend Issues**

#### **🔴 Frontend Not Loading**
```bash
# Symptoms
This site can't be reached (localhost:3000)

# Check frontend status
docker-compose logs frontend

# Solutions
# 1. Check if container is running
docker-compose ps

# 2. Restart frontend
docker-compose restart frontend

# 3. Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend

# 4. Check nginx configuration
docker-compose exec frontend cat /etc/nginx/nginx.conf
```

#### **🔴 API Calls Failing from Frontend**
```bash
# Symptoms
Network Error or 404 errors in browser console

# Solutions
# 1. Check backend URL in frontend code
# Should be: http://localhost:8001

# 2. Verify API endpoints exist
curl http://localhost:8001/docs

# 3. Check browser network tab for actual errors

# 4. Test API directly
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'
```

---

### **Performance Issues**

#### **🔴 Slow Response Times**
```bash
# Check resource usage
docker stats

# Check container logs for warnings
docker-compose logs | grep -i "warning\|error"

# Solutions
# 1. Increase container memory limits
# 2. Optimize database queries
# 3. Add caching where appropriate
# 4. Check disk space
df -h
```

#### **🔴 High Memory Usage**
```bash
# Check memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Solutions
# 1. Restart heavy containers
docker-compose restart milvus-standalone

# 2. Clean Docker system
docker system prune -f
docker volume prune -f

# 3. Limit container memory
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 1G
```

---

### **Development Issues**

#### **🔴 Python Module Import Errors**
```bash
# Symptoms
ModuleNotFoundError: No module named 'app'

# Solutions
# 1. Check Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/be"

# 2. Install in development mode
cd be
pip install -e .

# 3. Use absolute imports
from app.models.auth import User
# instead of
from models.auth import User
```

#### **🔴 Hot Reload Not Working**
```bash
# For backend (FastAPI)
# Use: uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# For frontend (React)
# Use: npm start
# Check if files are being watched

# Solutions
# 1. Check file permissions
# 2. Restart development server
# 3. Clear cache and restart
```

---

### **File & Environment Issues**

#### **🔴 .env File Issues**
```bash
# Symptoms
Configuration not being loaded

# Solutions
# 1. Check .env file location (should be in root directory)
ls -la .env

# 2. Check file format (no spaces around =)
# Correct: API_KEY=value
# Wrong: API_KEY = value

# 3. Check line endings (convert to Unix)
tr -d '\r' < .env > .env.tmp && mv .env.tmp .env

# 4. Verify variables are loaded
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### **🔴 File Permission Issues**
```bash
# Symptoms
Permission denied when accessing files

# Solutions
# 1. Fix script permissions
chmod +x docker-build.sh
chmod +x setup-docker.sh
chmod +x start.sh

# 2. Fix directory permissions
sudo chown -R $USER:$USER .

# 3. Fix uploaded file permissions
sudo chmod 755 be/data/uploads/
```

---

### **Production Issues**

#### **🔴 SSL/HTTPS Issues**
```bash
# For production deployment with SSL

# 1. Configure reverse proxy (nginx)
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
    }
}

# 2. Update CORS for production
allow_origins=["https://yourdomain.com"]
```

#### **🔴 Log Monitoring**
```bash
# Centralized logging setup
# 1. Use log aggregation (ELK stack, Fluentd)
# 2. Monitor error rates
# 3. Set up alerts for critical errors

# Basic log monitoring
docker-compose logs -f | grep -i error
```

---

## 🛠️ **Diagnostic Commands**

### **Health Check Commands**
```bash
# System health
./quick-fix.sh

# Service health
docker-compose ps
curl http://localhost:8001/health
curl http://localhost:3000

# Database health
docker-compose exec mongo mongosh --eval "db.adminCommand('ping')"
docker-compose exec redis redis-cli ping

# Milvus health
python -c "
from pymilvus import connections
connections.connect('default', host='localhost', port='19530')
print('Milvus OK')
"
```

### **Resource Monitoring**
```bash
# Container resources
docker stats

# Disk usage
docker system df
df -h

# Memory usage
free -h

# Network connections
ss -tulpn
```

### **Log Analysis**
```bash
# Recent errors
docker-compose logs --since 1h | grep -i error

# Service-specific logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f milvus-standalone

# Export logs
docker-compose logs > debug_logs.txt
```

---

## 📞 **Getting Help**

### **Before Asking for Help**
1. ✅ Check this troubleshooting guide
2. ✅ Check service logs: `docker-compose logs [service]`
3. ✅ Try restarting services: `docker-compose restart`
4. ✅ Check resource usage: `docker stats`
5. ✅ Verify configuration: `.env` file, ports, etc.

### **When Reporting Issues**
Include this information:
```bash
# System info
uname -a
docker --version
docker-compose --version

# Service status
docker-compose ps

# Recent logs
docker-compose logs --tail 50 [service-name]

# Configuration (without secrets)
cat .env | sed 's/=.*/=***HIDDEN***/'
```

### **Common Quick Fixes**
```bash
# Nuclear option (⚠️ will lose data)
docker-compose down
docker system prune -a -f
docker volume prune -f
# Then redeploy from scratch

# Quick restart
docker-compose restart

# Fix permissions
chmod +x *.sh
sudo chown -R $USER:$USER .

# Fix line endings
find . -name "*.sh" -exec dos2unix {} \;
```

---

**Remember:** Most issues can be resolved by checking logs, restarting services, or verifying configuration. When in doubt, start with the basics! 🚀
