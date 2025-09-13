#!/bin/bash

# 🚀 Quick Fix Script for Linux/WSL Docker Issues
# ===============================================

echo "🚀 Quick Fix cho Linux/WSL Docker Issues"
echo "========================================"

# Fix 1: Convert .env line endings
echo "▶️  Fixing .env line endings..."
if [ -f ".env" ]; then
    tr -d '\r' < .env > .env.tmp && mv .env.tmp .env
    echo "✅ Fixed .env line endings"
else
    echo "❌ .env file not found"
fi

# Fix 2: Make scripts executable
echo "▶️  Making scripts executable..."
chmod +x docker-build-fixed.sh fix-docker-permissions.sh 2>/dev/null || true
echo "✅ Scripts are now executable"

# Fix 3: Check Docker access
echo "▶️  Checking Docker access..."
if docker ps &>/dev/null; then
    echo "✅ Docker access OK"
    DOCKER_OK=true
else
    echo "❌ Docker access denied"
    echo "💡 Running permission fix..."
    
    # Try to add user to docker group
    if command -v sudo &>/dev/null; then
        sudo usermod -aG docker $USER 2>/dev/null || true
        echo "⚠️  User added to docker group. Please run: newgrp docker"
        echo "   Or restart your terminal/session"
    fi
    DOCKER_OK=false
fi

# Fix 4: Check Docker Compose
echo "▶️  Checking Docker Compose..."
if docker compose version &>/dev/null; then
    echo "✅ Docker Compose v2 available"
    COMPOSE_CMD="docker compose"
elif docker-compose --version &>/dev/null; then
    echo "✅ Docker Compose v1 available"  
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose not found"
    echo "💡 Please install: sudo apt-get install docker-compose-plugin"
    COMPOSE_CMD=""
fi

echo ""
echo "🎯 Quick Fix Summary:"
echo "===================="
echo "✅ Fixed .env line endings"
echo "✅ Made scripts executable"

if [ "$DOCKER_OK" = true ]; then
    echo "✅ Docker access working"
else
    echo "⚠️  Docker needs permission fix - run: newgrp docker"
fi

if [ -n "$COMPOSE_CMD" ]; then
    echo "✅ Docker Compose available: $COMPOSE_CMD"
else
    echo "❌ Docker Compose needs installation"
fi

echo ""
echo "🚀 Next Steps:"
if [ "$DOCKER_OK" = false ]; then
    echo "1. Run: newgrp docker  (or restart terminal)"
    echo "2. Test: docker ps"
    echo "3. Then run: ./docker-build-fixed.sh"
else
    echo "1. Run: ./docker-build-fixed.sh"
fi

echo ""
echo "🆘 If still having issues:"
echo "   - Run full fix: ./fix-docker-permissions.sh"
echo "   - Check guide: cat LINUX_DEPLOYMENT_FIX.md"
echo "   - Or use sudo: sudo ./docker-build-fixed.sh (not recommended)"
