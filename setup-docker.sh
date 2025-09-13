#!/bin/bash

# 🔧 Docker Setup Script for Ubuntu/Linux
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🔧 Docker Setup for Ubuntu/Linux"
echo "================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root/sudo"
    echo "💡 Run as regular user: ./setup-docker.sh"
    exit 1
fi

print_status "Current user: $(whoami)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_warning "Docker not installed. Installing..."
    
    # Update package index
    sudo apt-get update
    
    # Install required packages
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index again
    sudo apt-get update
    
    # Install Docker Engine
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    print_success "Docker installed successfully!"
else
    print_success "Docker is already installed"
fi

# Check if user is in docker group
if groups $USER | grep -q '\bdocker\b'; then
    print_success "User $(whoami) is already in docker group"
else
    print_status "Adding user $(whoami) to docker group..."
    sudo usermod -aG docker $USER
    print_success "User added to docker group"
    print_warning "IMPORTANT: Restart your terminal or run: newgrp docker"
fi

# Check for Docker Compose
if docker compose version &> /dev/null; then
    print_success "Docker Compose v2 is available"
elif docker-compose --version &> /dev/null; then
    print_success "Docker Compose v1 is available"
else
    print_status "Installing Docker Compose..."
    
    # Install Docker Compose plugin
    sudo apt-get install -y docker-compose-plugin
    
    print_success "Docker Compose installed successfully!"
fi

# Start Docker service
print_status "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Test Docker access
print_status "Testing Docker access..."
if docker ps &> /dev/null; then
    print_success "Docker access working!"
else
    print_warning "Docker access denied. Run: newgrp docker"
fi

echo ""
print_success "Docker Setup Complete!"
echo "======================"
print_success "Docker installed and configured"
print_success "User added to docker group"
print_success "Docker Compose available"
echo ""
echo "🚀 Next Steps:"
echo "1. Restart your terminal or run: newgrp docker"
echo "2. Test Docker: docker --version"
echo "3. Test Docker Compose: docker compose version"
echo "4. Run deployment: ./docker-build.sh"
echo ""
print_warning "If you still get permission errors, restart your computer"
