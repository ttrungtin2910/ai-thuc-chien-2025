#!/usr/bin/env python3
"""
Script to start Redis server using Docker for development
"""

import subprocess
import sys
import os
import time

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Docker found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker Desktop:")
        print("   Windows/Mac: https://www.docker.com/products/docker-desktop")
        print("   Linux: https://docs.docker.com/engine/install/")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(["docker", "compose", "version"], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Docker Compose found: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        # Try old docker-compose command
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✓ Docker Compose found: {result.stdout.strip()}")
            return "docker-compose"
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose not found. Please install Docker Compose.")
            return False

def check_redis_connection():
    """Check if Redis is already running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except:
        return False

def start_redis_docker():
    """Start Redis using Docker Compose"""
    try:
        # Check if Docker and Docker Compose are available
        if not check_docker():
            return False
            
        compose_cmd = check_docker_compose()
        if not compose_cmd:
            return False
        
        # Use appropriate command
        if compose_cmd == "docker-compose":
            cmd = ["docker-compose", "up", "-d", "redis"]
        else:
            cmd = ["docker", "compose", "up", "-d", "redis"]
        
        print("🚀 Starting Redis with Docker...")
        print("Command:", " ".join(cmd))
        print("-" * 50)
        
        result = subprocess.run(cmd, check=True)
        
        # Wait a moment for Redis to start
        print("⏳ Waiting for Redis to start...")
        for i in range(10):
            time.sleep(1)
            if check_redis_connection():
                print("✅ Redis is running successfully!")
                print("📍 Redis is available at: localhost:6379")
                print("🔧 To stop Redis: docker compose down")
                return True
            print(f"   Checking connection... ({i+1}/10)")
        
        print("⚠️  Redis container started but connection check failed.")
        print("   It might still be starting up. Check with: docker compose logs redis")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Redis: {e}")
        print("💡 Try running: docker compose logs redis")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def stop_redis_docker():
    """Stop Redis Docker container"""
    try:
        compose_cmd = check_docker_compose()
        if not compose_cmd:
            return False
            
        if compose_cmd == "docker-compose":
            cmd = ["docker-compose", "down"]
        else:
            cmd = ["docker", "compose", "down"]
            
        print("🛑 Stopping Redis Docker containers...")
        subprocess.run(cmd, check=True)
        print("✅ Redis containers stopped.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error stopping Redis: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop_redis_docker()
        return
    
    print("🔄 Checking Redis status...")
    if check_redis_connection():
        print("✅ Redis is already running on localhost:6379")
        print("💡 To restart: python start_redis.py stop && python start_redis.py")
        return
    
    print("📦 Redis not running. Starting with Docker...")
    success = start_redis_docker()
    
    if success:
        print("\n" + "="*60)
        print("🎉 Redis is ready for development!")
        print("📋 Next steps:")
        print("   1. Start Celery worker: python start_worker.py")
        print("   2. Start API server: python main.py")
        print("🔧 Management commands:")
        print("   • Stop Redis: python start_redis.py stop")
        print("   • View logs: docker compose logs redis")
        print("   • Redis CLI: docker exec -it dvc-ai-redis redis-cli")
        print("="*60)
    else:
        print("\n❌ Failed to start Redis. Please check Docker installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
