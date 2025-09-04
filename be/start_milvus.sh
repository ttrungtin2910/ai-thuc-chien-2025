#!/bin/bash

echo "🚀 Starting Milvus Vector Database for DVC.AI"
echo "=============================================="

# Change to docker directory
cd docker

echo ""
echo "📦 Starting Milvus with Docker Compose..."

# Create volumes directory if it doesn't exist
mkdir -p volumes/etcd
mkdir -p volumes/minio
mkdir -p volumes/milvus

# Start Milvus services
docker-compose -f docker-compose-milvus.yml up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 30

echo ""
echo "🔍 Checking service status..."
docker-compose -f docker-compose-milvus.yml ps

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



