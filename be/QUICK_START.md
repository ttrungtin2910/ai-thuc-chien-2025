# 🚀 Quick Start Guide - DVC.AI with OpenAI

## 📋 Prerequisites

1. **OpenAI API Key** (required)
2. **Docker & Docker Compose** (for Milvus)
3. **Python 3.8+** with conda/pip

## ⚡ Quick Setup

### 1️⃣ Setup OpenAI API Key
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Start Milvus Vector Database

**Windows:**
```cmd
start_milvus.bat
```

**Linux/macOS:**
```bash
./start_milvus.sh
```

### 4️⃣ Load Documents to Milvus
```bash
python scripts/load_documents_to_milvus.py
```

### 5️⃣ Start Backend Server
```bash
python main.py
```

### 6️⃣ Start Frontend (in new terminal)
```bash
cd ../fe
npm install
npm start
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Milvus UI**: http://localhost:3001
- **MinIO Console**: http://localhost:9001

## 🧪 Test RAG System

```bash
python scripts/test_rag_system.py
```

## 📱 Interactive Quick Start

```bash
python start_openai_system.py
```

---

**Need help?** Check `COMPLETE_GUIDE.md` for detailed instructions.
