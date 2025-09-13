@echo off
echo 🔄 Updating Backend Service
echo ===========================

echo ▶️  Rebuilding backend image...
docker-compose build backend

echo ▶️  Restarting backend service...
docker-compose up -d backend

echo ▶️  Restarting celery worker...
docker-compose restart celery-worker

echo ▶️  Checking service status...
docker-compose ps backend celery-worker

echo ✅ Backend update complete!
pause
