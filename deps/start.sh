#!/bin/bash

# 🚀 DVC.AI Start Script - Start existing Docker containers
# =========================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Starting DVC.AI Services"
echo "==========================="

# Check for docker compose
DOCKER_COMPOSE=""
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose --version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}❌ Docker Compose not found!${NC}"
    echo "Run setup first: ./setup-docker.sh"
    exit 1
fi

# Check if containers exist
if ! $DOCKER_COMPOSE ps | grep -q "dvc-ai"; then
    echo -e "${YELLOW}⚠️  No DVC.AI containers found${NC}"
    echo "Run full deployment first: ./docker-build.sh"
    exit 1
fi

# Start services
echo -e "${BLUE}▶️  Starting DVC.AI services...${NC}"
$DOCKER_COMPOSE up -d

# Wait for services
echo -e "${BLUE}▶️  Waiting for services to start...${NC}"
sleep 10

# Show status
echo -e "${BLUE}▶️  Service status:${NC}"
$DOCKER_COMPOSE ps

echo ""
echo -e "${GREEN}🎉 DVC.AI Services Started!${NC}"
echo "============================="
echo -e "${GREEN}✅ Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}✅ Backend API:${NC} http://localhost:8001"
echo -e "${GREEN}✅ API Documentation:${NC} http://localhost:8001/docs"
echo ""
echo "📋 Commands:"
echo "  $DOCKER_COMPOSE logs -f          # View logs"
echo "  $DOCKER_COMPOSE down             # Stop services"
echo "  $DOCKER_COMPOSE restart          # Restart services"