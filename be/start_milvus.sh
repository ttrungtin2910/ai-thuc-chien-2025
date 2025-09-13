#!/bin/bash

echo "🚀 Starting Milvus Vector Database for DVC.AI"
echo "=============================================="

# Check Docker Compose installation first
echo "🔍 Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install it first:"
    echo "   On Ubuntu: sudo apt-get install docker-compose-plugin"
    echo "   Or run: bash scripts/check_docker_compose.sh"
    exit 1
fi

# Change to docker directory
cd docker

echo ""
echo "📦 Starting Milvus with Docker Compose..."

# Create volumes directory if it doesn't exist
mkdir -p volumes/etcd
mkdir -p volumes/minio
mkdir -p volumes/milvus

# Start Milvus services
# Check if docker-compose (v1) or docker compose (v2) is available
if command -v docker-compose &> /dev/null; then
    echo "Using docker-compose (v1)..."
    docker-compose -f docker-compose-milvus.yml up -d
elif docker compose version &> /dev/null; then
    echo "Using docker compose (v2)..."
    docker compose -f docker-compose-milvus.yml up -d
else
    echo "❌ Error: Neither 'docker-compose' nor 'docker compose' command found!"
    echo "Please install Docker Compose or ensure Docker Desktop is running."
    exit 1
fi

echo ""
echo "⏳ Waiting for services to start..."
sleep 30

echo ""
echo "🔍 Checking service status..."
# Check service status with the same command format
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose-milvus.yml ps
elif docker compose version &> /dev/null; then
    docker compose -f docker-compose-milvus.yml ps
fi

echo ""
echo "🎉 Milvus Services Information:"
echo "======================================"
echo "🗄️  Milvus server: http://localhost:19530"
echo "🌐 Attu web UI: http://localhost:3001"
echo "📁 MinIO console: http://localhost:9001"
echo "======================================"
echo ""
echo "✅ Services are starting up. Please wait a moment before loading documents."
echo "📚 To load documents, run: python scripts/load_documents_to_milvus.py"
echo ""
echo "💡 Note: Make sure you have set OPENAI_API_KEY in your environment"
echo "   echo 'OPENAI_API_KEY=sk-your-key-here' > .env"
echo ""



