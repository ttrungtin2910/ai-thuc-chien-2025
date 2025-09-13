#!/bin/bash

# 🚀 DVC.AI Docker Deployment Script (Linux/WSL Compatible)
# ===========================================================

set -e  # Exit on any error

echo "🚀 DVC.AI Docker Deployment Script"
echo "=================================="

# Convert .env to Unix line endings if needed
if [ -f ".env" ]; then
    echo "▶️  Converting .env to Unix line endings..."
    tr -d '\r' < .env > .env.tmp && mv .env.tmp .env
fi

# Check if running with proper permissions
if ! docker --version &> /dev/null; then
    echo "❌ Docker not found or permission denied!"
    echo "💡 Solutions:"
    echo "   1. Install Docker: https://docs.docker.com/get-docker/"
    echo "   2. Add user to docker group: sudo usermod -aG docker $USER"
    echo "   3. Restart terminal/re-login after adding to group"
    echo "   4. Or run with sudo: sudo ./docker-build-fixed.sh"
    exit 1
fi

# Check for docker compose (v2) or docker-compose (v1)
DOCKER_COMPOSE=""
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
    echo "✅ Using Docker Compose v2"
elif docker-compose --version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo "✅ Using Docker Compose v1"
else
    echo "❌ Docker Compose not found!"
    echo "💡 Solutions:"
    echo "   1. Install Docker Compose v2: https://docs.docker.com/compose/install/"
    echo "   2. Or install v1: sudo apt-get install docker-compose"
    exit 1
fi

echo "▶️  Checking configuration..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "💡 Copy from .env.example: cp .env.example .env"
    exit 1
fi

echo "▶️  Building DVC.AI Docker containers..."

# Build images
echo "▶️  Building backend image..."
if ! docker build -t dvc-ai-backend ./be; then
    echo "❌ Backend build failed!"
    exit 1
fi

echo "▶️  Building frontend image..."
if ! docker build -t dvc-ai-frontend ./fe; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Docker images built successfully!"

echo "▶️  Starting DVC.AI services..."

# Stop existing containers
$DOCKER_COMPOSE down 2>/dev/null || true

# Start services
if ! $DOCKER_COMPOSE up --build -d; then
    echo "❌ Failed to start services!"
    echo "📋 Checking logs..."
    $DOCKER_COMPOSE logs
    exit 1
fi

echo "▶️  Waiting for services to start..."
sleep 10

echo "▶️  Checking service health..."
echo "Checking services..."
$DOCKER_COMPOSE ps

# Check if critical services are running
if ! $DOCKER_COMPOSE ps | grep -q "Up.*healthy.*backend"; then
    echo "⚠️  Backend service not healthy, checking logs..."
    $DOCKER_COMPOSE logs backend
fi

echo ""
echo "🎉 DVC.AI Deployment Complete!"
echo "================================"
echo "✅ Frontend: http://localhost:3000"
echo "✅ Backend API: http://localhost:8001"
echo "✅ API Documentation: http://localhost:8001/docs"
echo "✅ MongoDB: localhost:27017 (admin/dvcai2025)"
echo "✅ Redis: localhost:6379"
echo "✅ Milvus: localhost:19530"
echo ""
echo "📋 Useful Commands:"
echo "  $DOCKER_COMPOSE logs -f          # View all logs"
echo "  $DOCKER_COMPOSE logs -f backend  # View backend logs"
echo "  $DOCKER_COMPOSE logs -f frontend # View frontend logs"
echo "  $DOCKER_COMPOSE down             # Stop all services"
echo "  $DOCKER_COMPOSE restart          # Restart all services"
echo ""
echo "🔧 Troubleshooting:"
echo "  If services fail to start, check logs: $DOCKER_COMPOSE logs"
echo "  Ensure ports 3000, 8001, 27017, 6379, 19530 are available"
echo "  Verify .env configuration, especially OPENAI_API_KEY"
echo ""
echo "✅ Happy coding with DVC.AI! 🚀"
