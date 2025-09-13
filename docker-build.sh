#!/bin/bash

# DVC.AI - Docker Build and Deployment Script
# Script to build and deploy the complete DVC.AI system

echo "🚀 DVC.AI Docker Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${BLUE}▶️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.production .env
    print_warning "Please edit .env file with your configuration before continuing!"
    echo -e "${YELLOW}Required: Set OPENAI_API_KEY in .env file${NC}"
    read -p "Press Enter after configuring .env file..."
fi

# Check if OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    print_error "OPENAI_API_KEY is not configured in .env file!"
    print_warning "Please set your OpenAI API key in .env file"
    exit 1
fi

print_status "Building DVC.AI Docker containers..."

# Build images
print_status "Building backend image..."
docker build -t dvc-ai-backend:latest ./be

print_status "Building frontend image..."
docker build -t dvc-ai-frontend:latest ./fe

print_success "Docker images built successfully!"

# Deploy with Docker Compose
print_status "Starting DVC.AI services..."

# Stop existing containers if any
docker-compose down --remove-orphans

# Start services
docker-compose up -d --build

# Wait for services to start
print_status "Waiting for services to start..."
sleep 15

# Check service health
print_status "Checking service health..."

# Function to check if service is healthy
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start"
    return 1
}

# Check services
echo -n "Checking MongoDB..."
if docker-compose ps mongodb | grep -q "Up"; then
    print_success "MongoDB is running"
else
    print_error "MongoDB failed to start"
fi

echo -n "Checking Redis..."
if docker-compose ps redis | grep -q "Up"; then
    print_success "Redis is running"
else
    print_error "Redis failed to start"
fi

echo -n "Checking Milvus..."
if docker-compose ps milvus | grep -q "Up"; then
    print_success "Milvus is running"
else
    print_error "Milvus failed to start"
fi

echo -n "Checking Backend API..."
check_service "Backend API" "http://localhost:8001/health"

echo -n "Checking Frontend..."
check_service "Frontend" "http://localhost:3000"

# Show final status
echo
echo "🎉 DVC.AI Deployment Complete!"
echo "================================"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend API:${NC} http://localhost:8001"
echo -e "${GREEN}API Documentation:${NC} http://localhost:8001/docs"
echo -e "${GREEN}MongoDB:${NC} localhost:27017 (admin/dvcai2025)"
echo -e "${GREEN}Redis:${NC} localhost:6379"
echo -e "${GREEN}Milvus:${NC} localhost:19530"
echo
echo "📋 Useful Commands:"
echo "  docker-compose logs -f          # View all logs"
echo "  docker-compose logs -f backend  # View backend logs"
echo "  docker-compose logs -f frontend # View frontend logs"
echo "  docker-compose down             # Stop all services"
echo "  docker-compose restart          # Restart all services"
echo
echo "🔧 Troubleshooting:"
echo "  If services fail to start, check logs: docker-compose logs"
echo "  Ensure ports 3000, 8001, 27017, 6379, 19530 are available"
echo "  Verify .env configuration, especially OPENAI_API_KEY"
echo

print_success "Happy coding with DVC.AI! 🚀"
