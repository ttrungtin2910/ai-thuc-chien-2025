@echo off
echo 🚀 Starting DVC.AI Development Environment
echo =========================================

echo ▶️  Starting infrastructure services...
docker-compose up -d mongodb redis milvus etcd minio

echo ▶️  Waiting for services to be healthy...
timeout /t 10

echo ▶️  Starting development services with hot reload...
docker-compose -f docker-compose.dev.yml up --build

pause
