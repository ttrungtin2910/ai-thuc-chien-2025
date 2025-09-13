# Development Scripts

This directory contains separated development scripts for easier management:

## 📁 Scripts Overview

### 🐳 setup.py - Docker Dependencies Manager
Manages Docker-based dependencies only:
- MongoDB (Database)
- Redis (Cache & Session Storage)  
- Milvus (Vector Database)
- Attu (Milvus Admin UI)
- MinIO (Object Storage)

### ⚙️ run.py - Backend Services Runner
Manages backend services only:
- FastAPI Server (Backend API)
- Celery Worker (Background tasks)

## 🚀 Quick Start

### 1. Start Docker Dependencies
```bash
# Start all Docker services
cd be
python scripts/setup.py start

# Or start individual services
python scripts/setup.py mongodb
python scripts/setup.py redis
python scripts/setup.py milvus
```

### 2. Start Backend Services
```bash
# Start backend services (API + Celery)
python scripts/run.py start

# Or start individual services
python scripts/run.py api
python scripts/run.py worker
```

## 🔧 Available Commands

### setup.py Commands
| Command | Description |
|---------|-------------|
| `start` | Start all Docker services |
| `stop` | Stop all Docker services |
| `mongodb` | Start only MongoDB |
| `redis` | Start only Redis |
| `milvus` | Start only Milvus |
| `fix-mongodb` | Fix MongoDB authentication issues |
| `status` | Check Docker service status |
| `help` | Show help message |

### run.py Commands
| Command | Description |
|---------|-------------|
| `start` | Start backend services (API + Celery) |
| `api` | Start only API server |
| `worker` | Start only Celery worker |
| `stop` | Stop all backend services |
| `status` | Check backend service status |
| `help` | Show help message |

## 🔄 Typical Workflow

### Full Development Setup
```bash
# 1. Start Docker dependencies
python scripts/setup.py start

# 2. Wait for services to be ready, then start backend services
python scripts/run.py start
```

### Individual Service Development
```bash
# 1. Start Docker dependencies
python scripts/setup.py start

# 2. Start individual backend services
python scripts/run.py api
# or
python scripts/run.py worker
```

## 🆘 Troubleshooting

### MongoDB Authentication Issues
```bash
python scripts/setup.py fix-mongodb
```

### Check Service Status
```bash
# Check Docker services
python scripts/setup.py status

# Check backend services
python scripts/run.py status
```

## 🌐 Service URLs

### Docker Services
- **MongoDB**: `localhost:27017`
- **Redis**: `localhost:6379`
- **Milvus**: `localhost:19530`
- **Attu (Milvus Admin)**: `http://localhost:8080`
- **MinIO Console**: `http://localhost:9001`

### Backend Services
- **API Server**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

## 📋 Prerequisites

### For Docker Services (setup.py)
- Docker & Docker Compose
- Network access for downloading images

### For Backend Services (run.py)
- Python 3.8+
- Required Python packages (see requirements.txt)
- Redis (started via setup.py)

## ⚠️ Migration from dev.py

The old `dev.py` script has been split into these two specialized scripts:

- **Before**: `python scripts/dev.py start` 
- **Now**: 
  ```bash
  python scripts/setup.py start    # Start Docker services
  python scripts/run.py start      # Start backend services
  ```

This separation provides:
- ✅ Clearer responsibility separation
- ✅ Faster development iteration
- ✅ Better error isolation
- ✅ Easier troubleshooting
