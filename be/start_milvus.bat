@echo off
echo 🚀 Starting Milvus Vector Database for DVC.AI
echo ==============================================

REM Change to docker directory
cd docker

echo.
echo 📦 Starting Milvus with Docker Compose...

REM Create volumes directory if it doesn't exist
if not exist "volumes" mkdir volumes
if not exist "volumes\etcd" mkdir volumes\etcd
if not exist "volumes\minio" mkdir volumes\minio
if not exist "volumes\milvus" mkdir volumes\milvus

REM Start Milvus services
docker-compose -f docker-compose-milvus.yml up -d

echo.
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak > nul

echo.
echo 🔍 Checking service status...
docker-compose -f docker-compose-milvus.yml ps

echo.
echo 🎉 Milvus Services Information:
echo ======================================
echo 🗄️  Milvus server: http://localhost:19530
echo 🌐 Attu web UI: http://localhost:3001
echo 📁 MinIO console: http://localhost:9001
echo ======================================
echo.
echo ✅ Services are starting up. Please wait a moment before loading documents.
echo 📚 To load documents, run: python scripts/load_documents_to_milvus.py
echo.
echo 💡 Note: Make sure you have set OPENAI_API_KEY in your environment
echo    echo OPENAI_API_KEY=sk-your-key-here > .env
echo.
pause



