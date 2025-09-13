@echo off
REM DVC.AI - Docker Build and Deployment Script for Windows
REM Script to build and deploy the complete DVC.AI system

echo 🚀 DVC.AI Docker Deployment Script
echo ==================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose is not installed. Please install Docker Compose first.
        pause
        exit /b 1
    )
)

echo ▶️  Checking configuration...

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.production .env
    echo ⚠️  Please edit .env file with your configuration before continuing!
    echo Required: Set OPENAI_API_KEY in .env file
    pause
)

echo ▶️  Building DVC.AI Docker containers...

REM Build backend image
echo ▶️  Building backend image...
docker build -t dvc-ai-backend:latest ./be
if errorlevel 1 (
    echo ❌ Failed to build backend image
    pause
    exit /b 1
)

REM Build frontend image
echo ▶️  Building frontend image...
docker build -t dvc-ai-frontend:latest ./fe
if errorlevel 1 (
    echo ❌ Failed to build frontend image
    pause
    exit /b 1
)

echo ✅ Docker images built successfully!

REM Deploy with Docker Compose
echo ▶️  Starting DVC.AI services...

REM Stop existing containers if any
docker-compose down --remove-orphans

REM Start services
docker-compose up -d --build
if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

REM Wait for services to start
echo ▶️  Waiting for services to start...
timeout /t 15 /nobreak > nul

echo ▶️  Checking service health...

REM Check if services are running
echo Checking services...
docker-compose ps

echo.
echo 🎉 DVC.AI Deployment Complete!
echo ================================
echo ✅ Frontend: http://localhost:3000
echo ✅ Backend API: http://localhost:8001
echo ✅ API Documentation: http://localhost:8001/docs
echo ✅ MongoDB: localhost:27017 (admin/dvcai2025)
echo ✅ Redis: localhost:6379
echo ✅ Milvus: localhost:19530
echo.
echo 📋 Useful Commands:
echo   docker-compose logs -f          # View all logs
echo   docker-compose logs -f backend  # View backend logs
echo   docker-compose logs -f frontend # View frontend logs
echo   docker-compose down             # Stop all services
echo   docker-compose restart          # Restart all services
echo.
echo 🔧 Troubleshooting:
echo   If services fail to start, check logs: docker-compose logs
echo   Ensure ports 3000, 8001, 27017, 6379, 19530 are available
echo   Verify .env configuration, especially OPENAI_API_KEY
echo.
echo ✅ Happy coding with DVC.AI! 🚀

pause
