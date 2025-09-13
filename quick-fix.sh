#!/bin/bash

# 🚀 Quick Fix Script for Common Ubuntu/Linux Issues
# ==================================================

echo "🚀 Quick Fix for DVC.AI Deployment"
echo "==================================="

# Fix 1: Convert .env line endings
if [ -f ".env" ]; then
    echo "▶️  Fixing .env line endings..."
    tr -d '\r' < .env > .env.tmp && mv .env.tmp .env
    echo "✅ Fixed .env line endings"
fi

# Fix 2: Make scripts executable
echo "▶️  Making scripts executable..."
chmod +x *.sh 2>/dev/null || true
echo "✅ Scripts are now executable"

# Fix 3: Quick Docker permission check
echo "▶️  Checking Docker access..."
if docker ps &>/dev/null; then
    echo "✅ Docker access OK"
    echo ""
    echo "🎯 Ready to deploy! Run: ./docker-build.sh"
else
    echo "❌ Docker access denied"
    echo ""
    echo "🔧 Quick fixes:"
    echo "1. Run setup: ./setup-docker.sh"
    echo "2. Add to group: sudo usermod -aG docker $USER && newgrp docker"
    echo "3. Restart terminal"
fi

echo ""
echo "📋 Available commands:"
echo "  ./docker-build.sh    # Full deployment"
echo "  ./setup-docker.sh    # Setup Docker & permissions"
echo "  ./start.sh           # Start existing containers"