#!/bin/bash

# =================================================================
# Production Configuration Script for DVC.AI
# =================================================================

echo "============================================================"
echo "🚀 DVC.AI Production Configuration"
echo "============================================================"

# Set internal IP for production
echo "📡 Using Internal IP for production deployment..."
SERVER_IP="10.128.0.4"

echo "🖥️  Production Server IP: $SERVER_IP"
echo ""

# Confirm IP address
read -p "Use this internal IP (10.128.0.4) for production? [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    read -p "Enter your server IP address: " SERVER_IP
fi

echo ""
echo "🔧 Configuring frontend for IP: $SERVER_IP"

# Create frontend production environment file
cat > fe/.env.production << EOF
# Production Environment Configuration
# Generated on $(date)

REACT_APP_API_URL=http://${SERVER_IP}:8001
REACT_APP_WS_URL=http://${SERVER_IP}:8001

# Production optimizations
GENERATE_SOURCEMAP=false
REACT_APP_ENV=production
EOF

echo "✅ Created fe/.env.production"

# Update backend CORS if needed
if [ -f "be/.env" ]; then
    if ! grep -q "WEBSOCKET_CORS_ORIGINS.*${SERVER_IP}" be/.env; then
        echo ""
        echo "🔧 Updating backend CORS configuration..."
        
        # Backup original
        cp be/.env be/.env.backup
        
        # Update CORS origins
        sed -i.bak "s/WEBSOCKET_CORS_ORIGINS=.*/WEBSOCKET_CORS_ORIGINS=http:\/\/${SERVER_IP}:3000,http:\/\/localhost:3000/g" be/.env
        
        echo "✅ Updated backend CORS for production"
    fi
fi

echo ""
echo "============================================================"
echo "🎉 Configuration Complete!"
echo "============================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Build frontend:     cd fe && npm run build"
echo "2. Start backend:      cd be && python scripts/setup.py start"
echo "3. Start API server:   cd be && python main.py"
echo "4. Serve frontend:     cd fe && npx serve -s build -p 3000"
echo ""
echo "🌐 Access your app at: http://${SERVER_IP}:3000"
echo "📚 API docs at:        http://${SERVER_IP}:8001/docs"
echo ""
echo "📖 For more details, see: DEPLOYMENT_GUIDE.md"
echo ""
