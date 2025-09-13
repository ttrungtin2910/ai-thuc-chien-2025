#!/bin/bash

# 🚀 DVC.AI Docker Deployment Script for Ubuntu/Linux
# ====================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

echo "🚀 DVC.AI Docker Deployment Script"
echo "=================================="

# Convert .env to Unix line endings if needed
if [ -f ".env" ]; then
    print_status "Converting .env to Unix line endings..."
    tr -d '\r' < .env > .env.tmp && mv .env.tmp .env
fi

# Check if running with proper permissions
if ! docker --version &> /dev/null; then
    print_error "Docker not found or permission denied!"
    echo "💡 Solutions:"
    echo "   1. Install Docker: https://docs.docker.com/get-docker/"
    echo "   2. Add user to docker group: sudo usermod -aG docker $USER"
    echo "   3. Restart terminal/re-login after adding to group"
    echo "   4. Run setup script: ./setup-docker.sh"
    exit 1
fi

# Check for docker compose (v2) or docker-compose (v1)
DOCKER_COMPOSE=""
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
    print_success "Using Docker Compose v2"
elif docker-compose --version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    print_success "Using Docker Compose v1"
else
    print_error "Docker Compose not found!"
    echo "💡 Solutions:"
    echo "   1. Install Docker Compose: sudo apt-get install docker-compose-plugin"
    echo "   2. Or run setup script: ./setup-docker.sh"
    exit 1
fi

print_status "Checking configuration..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    if [ -f "be/env.example" ]; then
        print_warning "Copy from template: cp be/env.example .env"
    else
        print_warning "Create .env file with your configuration"
    fi
    exit 1
fi

# Check if OPENAI_API_KEY is set (optional but recommended)
if grep -q "OPENAI_API_KEY=sk-" .env; then
    print_success "OpenAI API key configured"
else
    print_warning "OpenAI API key not configured - some features may not work"
fi

print_status "Building DVC.AI Docker containers..."

# Build images
print_status "Building backend image..."
if ! docker build -t dvc-ai-backend ./be; then
    print_error "Backend build failed!"
    exit 1
fi

print_status "Building frontend image..."
if ! docker build -t dvc-ai-frontend ./fe; then
    print_error "Frontend build failed!"
    exit 1
fi

print_success "Docker images built successfully!"

print_status "Starting DVC.AI services..."

# Stop existing containers
$DOCKER_COMPOSE down 2>/dev/null || true

# Start services
if ! $DOCKER_COMPOSE up --build -d; then
    print_error "Failed to start services!"
    print_status "Checking logs..."
    $DOCKER_COMPOSE logs
    exit 1
fi

print_status "Waiting for services to start..."
sleep 15

print_status "Checking service health..."
$DOCKER_COMPOSE ps

# Check if critical services are running
if $DOCKER_COMPOSE ps | grep -q "Up.*healthy.*backend"; then
    print_success "Backend service is healthy"
else
    print_warning "Backend service not healthy yet, checking logs..."
    $DOCKER_COMPOSE logs backend | tail -20
fi

# Health check function
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "$service_name is responding"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_warning "$service_name not responding yet (may still be starting)"
    return 1
}

# Test endpoints
echo -n "Testing Backend API..."
check_service "Backend API" "http://localhost:8001/health"

echo -n "Testing Frontend..."
check_service "Frontend" "http://localhost:3000"

echo ""
echo "🎉 DVC.AI Deployment Complete!"
echo "================================"
print_success "Frontend: http://localhost:3000"
print_success "Backend API: http://localhost:8001"
print_success "API Documentation: http://localhost:8001/docs"
print_success "MongoDB: localhost:27017 (admin/dvcai2025)"
print_success "Redis: localhost:6379"
print_success "Milvus: localhost:19530"
echo ""
echo "📋 Useful Commands:"
echo "  $DOCKER_COMPOSE logs -f          # View all logs"
echo "  $DOCKER_COMPOSE logs -f backend  # View backend logs"
echo "  $DOCKER_COMPOSE logs -f frontend # View frontend logs"
echo "  $DOCKER_COMPOSE down             # Stop all services"
echo "  $DOCKER_COMPOSE restart          # Restart all services"
echo ""
echo "🔧 Troubleshooting:"
echo "  If services fail to start, check: $DOCKER_COMPOSE logs"
echo "  Ensure ports 3000, 8001, 27017, 6379, 19530 are available"
echo "  Run setup if needed: ./setup-docker.sh"
echo ""
print_success "Happy coding with DVC.AI! 🚀"