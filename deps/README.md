# 🛠️ DVC.AI Dependencies & Setup

This directory contains all setup scripts and dependencies for DVC.AI project environment.

## 📁 **Structure**

```
deps/
├── setup.py            # Main Python setup script (cross-platform)
├── setup-docker.sh     # Docker environment setup (Linux/macOS)  
├── docker-build.sh     # Build and deployment script
├── start.sh            # Start existing services
└── README.md           # This file
```

---

## 🚀 **Quick Setup**

### **Option 1: Python Setup (Recommended)**
```bash
# Complete environment setup
cd deps
python setup.py

# Specific operations
python setup.py --help      # Show all options
python setup.py --deps      # Install dependencies only
python setup.py --start     # Start services only
python setup.py --stop      # Stop all services
python setup.py --status    # Show service status
```

### **Option 2: Shell Scripts (Linux/macOS)**
```bash
cd deps

# 1. First-time Docker setup
./setup-docker.sh

# 2. Build and deploy
./docker-build.sh

# 3. Daily operations
./start.sh
```

---

## 🎯 **Usage Scenarios**

### **🆕 First Time Setup**
```bash
# Complete setup from scratch
cd deps
python setup.py
```

### **🔄 Development Mode**
```bash
# Start development environment
cd deps
python setup.py --start

# Stop when done
python setup.py --stop
```

### **🐳 Docker-only Setup**
```bash
cd deps
./setup-docker.sh          # Setup Docker
./docker-build.sh          # Deploy
```

### **⚡ Quick Start (existing environment)**
```bash
cd deps
./start.sh
```

---

## 📋 **Prerequisites**

### **Required:**
- Python 3.8+ (for setup.py)
- Docker & Docker Compose
- 4GB RAM, 20GB disk space

### **Optional:**
- OpenAI API Key (for AI features)
- Google Cloud credentials (for cloud storage)

---

## ⚙️ **Environment Configuration**

Before running setup, configure your environment:

```bash
# Copy template to root directory
cp ../be/env.example ../.env

# Edit configuration
nano ../.env
```

**Required variables:**
```env
OPENAI_API_KEY=sk-your-api-key-here
SECRET_KEY=your-secret-key
```

---

## 🔧 **Troubleshooting**

### **Common Issues:**

| Problem | Solution |
|---------|----------|
| Python script fails | Check Python 3.8+ installed |
| Docker permission denied | Run `./setup-docker.sh` |
| Port already in use | Stop conflicting services |
| Services not starting | Check `docker compose logs` |

### **Get Help:**
```bash
# Python setup help
python setup.py --help

# Check service status
python setup.py --status

# Manual cleanup
docker compose down
docker system prune -f
```

---

## 📖 **Script Details**

### **setup.py**
- **Purpose:** Cross-platform setup automation
- **Features:** Dependencies, services, configuration
- **Platform:** Windows, Linux, macOS
- **Output:** Full environment ready

### **setup-docker.sh**
- **Purpose:** Docker environment setup
- **Features:** Install Docker, permissions, Compose
- **Platform:** Linux, macOS
- **Output:** Docker ready for use

### **docker-build.sh**  
- **Purpose:** Build and deploy application
- **Features:** Build images, start services, health checks
- **Platform:** Linux, macOS
- **Output:** Running DVC.AI application

### **start.sh**
- **Purpose:** Start existing containers
- **Features:** Quick startup, status check
- **Platform:** Linux, macOS  
- **Output:** Services running

---

## 🔗 **Access Points**

After successful setup:

- 🎨 **Frontend:** http://localhost:3000
- ⚙️ **Backend API:** http://localhost:8001
- 📖 **API Docs:** http://localhost:8001/docs
- 🗄️ **MongoDB:** localhost:27017
- 🔍 **Milvus:** localhost:19530

---

**📚 For detailed documentation, see [`../docs/`](../docs/) directory.**
