@echo off
echo 🔄 Updating Frontend Service
echo ============================

echo ▶️  Rebuilding frontend image...
docker-compose build frontend

echo ▶️  Restarting frontend service...
docker-compose up -d frontend

echo ▶️  Checking service status...
docker-compose ps frontend

echo ✅ Frontend update complete!
echo 🌐 Frontend available at: http://localhost:3000

pause
