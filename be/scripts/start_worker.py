#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to start Celery worker for document processing
"""

import subprocess
import sys
import os

def check_redis_connection():
    """Check if Redis is available"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except Exception as e:
        print(f"ERROR: Redis connection failed: {e}")
        return False

def start_worker():
    """Start Celery worker"""
    try:
        # Make sure we're in the backend directory (parent of scripts)
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(scripts_dir)  # Go up one level to be/
        os.chdir(backend_dir)
        
        print("Starting Celery worker...")
        print("Checking Redis connection...")
        
        # Check Redis connection first
        if not check_redis_connection():
            print("ERROR: Redis is not running!")
            print("Start Redis first: python start_redis.py")
            print("Or use: python dev.py start")
            return
        
        print("Redis connection OK")
        print("Press Ctrl+C to stop the worker")
        print("-" * 50)
        
        # Start Celery worker (Celery 5.0+ syntax) with solo pool for Windows
        cmd = [
            sys.executable, "-m", "celery", 
            "-A", "app.workers.celery_app.celery_app",
            "worker",
            "--loglevel=info",
            "--pool=threads",  # Use threads pool instead of prefork  
            "--concurrency=2"
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\nStopping Celery worker...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting Celery worker: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_worker()
