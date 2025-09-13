#!/bin/bash

# 🔧 Docker Permissions Fix Script
# =================================

echo "🔧 Fixing Docker Permissions and Installation"
echo "============================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please don't run this script as root/sudo"
    echo "💡 Run as regular user: ./fix-docker-permissions.sh"
    exit 1
fi

echo "▶️  Current user: $(whoami)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed!"
    echo "▶️  Installing Docker..."
    
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
    
    echo "✅ Docker installed successfully!"
else
    echo "✅ Docker is already installed"
fi

# Check if user is in docker group
if groups $USER | grep -q '\bdocker\b'; then
    echo "✅ User $(whoami) is already in docker group"
else
    echo "▶️  Adding user $(whoami) to docker group..."
    sudo usermod -aG docker $USER
    echo "✅ User added to docker group"
    echo "⚠️  IMPORTANT: You need to log out and log back in (or restart terminal)"
    echo "   Or run: newgrp docker"
fi

# Check for Docker Compose
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose v2 is available"
elif docker-compose --version &> /dev/null; then
    echo "✅ Docker Compose v1 is available"
else
    echo "▶️  Installing Docker Compose v2..."
    
    # Docker Compose v2 is usually included with Docker Desktop
    # For Linux servers, install plugin
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    
    # Download Docker Compose
    sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
    
    # Make executable
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symlink for v2 syntax
    sudo ln -sf /usr/local/bin/docker-compose $DOCKER_CONFIG/cli-plugins/docker-compose
    
    echo "✅ Docker Compose installed successfully!"
fi

# Start Docker service
echo "▶️  Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

echo ""
echo "🎉 Docker Setup Complete!"
echo "========================="
echo "✅ Docker installed and configured"
echo "✅ User added to docker group"
echo "✅ Docker Compose available"
echo ""
echo "🔄 Next Steps:"
echo "1. Restart your terminal or run: newgrp docker"
echo "2. Test Docker: docker --version"
echo "3. Test Docker Compose: docker compose version"
echo "4. Run deployment: ./docker-build-fixed.sh"
echo ""
echo "⚠️  If you still get permission errors:"
echo "   - Log out and log back in completely"
echo "   - Or restart your computer"
echo "   - Or run: sudo ./docker-build-fixed.sh (not recommended)"
