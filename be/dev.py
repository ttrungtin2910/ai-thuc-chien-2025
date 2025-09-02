#!/usr/bin/env python3
"""
Development environment management script
Easily start/stop all required services for development
"""

import subprocess
import sys
import os
import time
import signal
import threading
from concurrent.futures import ThreadPoolExecutor

class DevEnvironment:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def run_command(self, cmd, name, cwd=None):
        """Run a command in a separate process"""
        try:
            print(f"🚀 Starting {name}...")
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append((process, name))
            
            # Stream output
            for line in process.stdout:
                if self.running:
                    print(f"[{name}] {line.rstrip()}")
                else:
                    break
                    
        except Exception as e:
            print(f"❌ Error starting {name}: {e}")
    
    def check_redis_connection(self):
        """Check if Redis is available"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            return True
        except:
            return False
    
    def start_redis(self):
        """Start Redis with Docker"""
        print("📦 Starting Redis with Docker...")
        
        # Check if already running
        if self.check_redis_connection():
            print("✅ Redis is already running")
            return True
            
        # Start Redis container
        try:
            cmd = ["docker", "compose", "up", "-d", "redis"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Wait for Redis to be ready
            print("⏳ Waiting for Redis to start...")
            for i in range(15):
                time.sleep(1)
                if self.check_redis_connection():
                    print("✅ Redis is ready!")
                    return True
                print(f"   Checking Redis... ({i+1}/15)")
            
            print("⚠️  Redis container started but not responding")
            return False
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start Redis: {e}")
            return False
    
    def start_celery_worker(self):
        """Start Celery worker in background"""
        cmd = [
            sys.executable, "-m", "celery",
            "-A", "celery_app.celery_app",
            "worker",
            "--loglevel=info",
            "--concurrency=2"
        ]
        
        thread = threading.Thread(
            target=self.run_command,
            args=(cmd, "Celery Worker"),
            daemon=True
        )
        thread.start()
        return thread
    
    def start_api_server(self):
        """Start FastAPI server in background"""
        cmd = [sys.executable, "main.py"]
        
        thread = threading.Thread(
            target=self.run_command,
            args=(cmd, "API Server"),
            daemon=True
        )
        thread.start()
        return thread
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        # Terminate all processes
        for process, name in self.processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"   Error stopping {name}: {e}")
        
        # Stop Redis container
        try:
            subprocess.run(["docker", "compose", "down"], 
                         check=True, capture_output=True)
            print("   ✅ Redis container stopped")
        except:
            print("   ⚠️  Could not stop Redis container")
        
        print("✅ All services stopped")
    
    def start_all(self):
        """Start all development services"""
        print("🚀 Starting DVC.AI Development Environment")
        print("=" * 60)
        
        # 1. Start Redis
        if not self.start_redis():
            print("❌ Failed to start Redis")
            return False
        
        time.sleep(2)
        
        # 2. Start Celery Worker
        print("\n📋 Starting Celery Worker...")
        self.start_celery_worker()
        time.sleep(3)
        
        # 3. Start API Server
        print("\n🌐 Starting API Server...")
        self.start_api_server()
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("🎉 Development environment is ready!")
        print("📍 API Server: http://localhost:8000")
        print("📍 Redis: localhost:6379")
        print("📋 Swagger UI: http://localhost:8000/docs")
        print("🔧 Press Ctrl+C to stop all services")
        print("=" * 60)
        
        return True

def show_help():
    """Show help message"""
    print("""
DVC.AI Development Environment Manager

Commands:
    start       Start all services (Redis, Celery, API)
    stop        Stop all services
    redis       Start only Redis
    worker      Start only Celery worker
    api         Start only API server
    status      Check service status
    logs        Show Redis logs
    help        Show this help message

Examples:
    python dev.py start     # Start all services
    python dev.py stop      # Stop all services
    python dev.py redis     # Start only Redis
""")

def check_status():
    """Check status of services"""
    print("🔍 Checking service status...")
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis: Running")
    except:
        print("❌ Redis: Not running")
    
    # Check API server
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            print("✅ API Server: Running")
        else:
            print("⚠️  API Server: Responding but status unclear")
    except:
        print("❌ API Server: Not running")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    env = DevEnvironment()
    
    try:
        if command == "start":
            if env.start_all():
                # Keep running until Ctrl+C
                try:
                    while env.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                finally:
                    env.stop_all()
        
        elif command == "stop":
            env.stop_all()
        
        elif command == "redis":
            env.start_redis()
        
        elif command == "worker":
            if not env.check_redis_connection():
                print("❌ Redis not running. Start Redis first: python dev.py redis")
                return
            env.start_celery_worker()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                env.stop_all()
        
        elif command == "api":
            env.start_api_server()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                env.stop_all()
        
        elif command == "status":
            check_status()
        
        elif command == "logs":
            subprocess.run(["docker", "compose", "logs", "-f", "redis"])
        
        elif command == "help":
            show_help()
        
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
    
    except KeyboardInterrupt:
        env.stop_all()
    except Exception as e:
        print(f"❌ Error: {e}")
        env.stop_all()

if __name__ == "__main__":
    main()
