#!/usr/bin/env python3
"""
Backend services runner script
Manages Python-based backend services (API server, Celery worker)
"""

import subprocess
import sys
import os
import time
import signal
import threading
import platform
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def colored(text, color):
        return f"{color}{text}{Colors.END}"


class BackendRunner:
    def __init__(self):
        self.processes = []
        self.running = True
        self.project_root = Path(__file__).parent.parent.parent  # Go up to project root
        self.is_windows = platform.system().lower() == 'windows'
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(Colors.colored(f"⚙️ {title}", Colors.BOLD + Colors.CYAN))
        print("="*60)
    
    def print_step(self, message):
        """Print formatted step"""
        print(f"\n{Colors.colored('▶', Colors.BOLD + Colors.BLUE)} {message}")
    
    def print_success(self, message):
        """Print success message"""
        print(Colors.colored(f"✅ {message}", Colors.GREEN))
    
    def print_error(self, message):
        """Print error message"""
        print(Colors.colored(f"❌ {message}", Colors.RED))
    
    def print_warning(self, message):
        """Print warning message"""
        print(Colors.colored(f"⚠️ {message}", Colors.YELLOW))
    
    def print_info(self, message):
        """Print info message"""
        print(Colors.colored(f"💡 {message}", Colors.CYAN))
        
    def run_command(self, cmd, name, cwd=None, shell=False, check=True, capture_output=False, timeout=None):
        """Run a command with proper error handling"""
        try:
            if capture_output:
                if isinstance(cmd, str) and not shell:
                    cmd = cmd.split()
                
                result = subprocess.run(
                    cmd, 
                    shell=shell, 
                    check=check, 
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout,
                    cwd=cwd
                )
                return result
            else:
                # For streaming output (services)
                self.print_step(f"Starting {name}...")
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    shell=shell
                )
                
                self.processes.append((process, name))
                
                # Stream output
                for line in process.stdout:
                    if self.running:
                        print(f"[{Colors.colored(name, Colors.BOLD)}] {line.rstrip()}")
                    else:
                        break
                        
        except subprocess.CalledProcessError as e:
            if capture_output:
                return e
            self.print_error(f"Error starting {name}: {e}")
        except subprocess.TimeoutExpired:
            self.print_error(f"Command timed out: {name}")
            return None
        except Exception as e:
            self.print_error(f"Error starting {name}: {e}")
    
    def check_service_running(self, service_name, port):
        """Check if a service is running on specified port"""
        try:
            if self.is_windows:
                result = self.run_command(
                    f"netstat -an | findstr :{port}", 
                    service_name,
                    shell=True, 
                    capture_output=True,
                    check=False
                )
            else:
                result = self.run_command(
                    ["nc", "-z", "localhost", str(port)], 
                    service_name,
                    capture_output=True,
                    check=False
                )
            
            return result and result.returncode == 0
        except:
            return False

    def check_redis_connection(self):
        """Check if Redis is available"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            return True
        except:
            return False

    def check_mongodb_connection(self):
        """Check if MongoDB is available with authentication"""
        try:
            import os
            from pymongo import MongoClient
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv()
            
            # Get MongoDB URL from environment variables
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:dvcai2025@localhost:27017/dvc_ai_db?authSource=admin")
            
            client = MongoClient(
                mongodb_url, 
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000
            )
            # Test the connection
            client.admin.command('ping')
            client.close()
            return True
        except Exception as e:
            return False
    
    def start_celery_worker(self):
        """Start Celery worker in background"""
        cmd = [
            sys.executable, "-m", "celery",
            "-A", "app.workers.celery_app.celery_app",
            "worker",
            "--loglevel=info",
            "--concurrency=2"
        ]
        
        thread = threading.Thread(
            target=self.run_command,
            args=(cmd, "Celery Worker"),
            kwargs={"cwd": self.project_root / "be"},
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
            kwargs={"cwd": self.project_root / "be"},
            daemon=True
        )
        thread.start()
        return thread



    
    def stop_all(self):
        """Stop all processes"""
        self.print_header("Stopping Backend Services")
        self.running = False
        
        # Terminate all processes
        for process, name in self.processes:
            try:
                self.print_info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                self.print_error(f"Error stopping {name}: {e}")
        
        self.print_success("Backend services stopped")
    
    def start_backend(self):
        """Start backend services (API + Celery)"""
        self.print_header("Backend Services")
        
        # Check dependencies
        if not self.check_redis_connection():
            self.print_error("Redis not running. Please run 'python scripts/setup.py start' first")
            return False
        
        if not self.check_mongodb_connection():
            self.print_warning("MongoDB authentication check failed - continuing anyway")
        
        # 1. Start Celery Worker
        self.print_step("Starting Celery Worker...")
        self.start_celery_worker()
        time.sleep(3)
        
        # 2. Start API Server
        self.print_step("Starting API Server...")
        self.start_api_server()
        time.sleep(3)
        
        # Show service information
        self.show_service_info()
        
        self.print_header("Backend Services Ready! 🎉")
        self.print_info("Press Ctrl+C to stop all services")
        
        return True
    
    
    def show_service_info(self):
        """Show information about running backend services"""
        self.print_header("Backend Service Information")
        
        # Backend services
        backend_services = [
            ("API Server", 8000, "FastAPI Backend", "http://localhost:8000"),
            ("Swagger UI", 8000, "API Documentation", "http://localhost:8000/docs")
        ]
        
        print(Colors.colored("⚙️ Backend Services:", Colors.BOLD + Colors.GREEN))
        for name, port, description, url in backend_services:
            # These are application services, assume running if started
            status = "🟢"
            print(f"  {status} {Colors.colored(name, Colors.BOLD)}: {url}")
            print(f"     {description}")

def show_help():
    """Show help message"""
    runner = BackendRunner()
    runner.print_header("Backend Services Runner")
    
    commands = [
        ("start", "Start backend services (API + Celery)"),
        ("api", "Start only API server"),
        ("worker", "Start only Celery worker"),
        ("stop", "Stop all backend services"),
        ("status", "Check backend service status"),
        ("help", "Show this help message")
    ]
    
    print(Colors.colored("Commands:", Colors.BOLD + Colors.YELLOW))
    for cmd, desc in commands:
        print(f"  {Colors.colored(cmd, Colors.BOLD + Colors.GREEN):<12} {desc}")
    
    print(f"\n{Colors.colored('Examples:', Colors.BOLD + Colors.YELLOW)}")
    examples = [
        ("python scripts/run.py start", "Start backend services"),
        ("python scripts/run.py api", "Start only API server"),
        ("python scripts/run.py worker", "Start only Celery worker"),
        ("python scripts/run.py stop", "Stop all services")
    ]
    
    for cmd, desc in examples:
        print(f"  {Colors.colored(cmd, Colors.CYAN):<30} # {desc}")

def check_status():
    """Check status of backend services"""
    runner = BackendRunner()
    runner.print_header("Backend Service Status Check")
    
    # Check API server
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            runner.print_success("API Server: Running and responding")
        else:
            runner.print_warning("API Server: Responding but status unclear")
    except:
        runner.print_error("API Server: Not running or not responding")
    
    # Check Redis connection
    if runner.check_redis_connection():
        runner.print_success("Redis: Connection successful")
    else:
        runner.print_error("Redis: Not available (needed for Celery)")
    
    # Check MongoDB connection
    if runner.check_mongodb_connection():
        runner.print_success("MongoDB: Connection successful")
    else:
        runner.print_warning("MongoDB: Connection failed")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    runner = BackendRunner()
    
    try:
        if command in ["start", "backend"]:
            if runner.start_backend():
                # Keep running until Ctrl+C
                try:
                    while runner.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                finally:
                    runner.stop_all()
        
        elif command == "api":
            runner.start_api_server()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                runner.stop_all()
        
        elif command == "worker":
            if not runner.check_redis_connection():
                runner.print_error("Redis not running. Start Redis first: python scripts/setup.py redis")
                return
            runner.start_celery_worker()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                runner.stop_all()
        
        elif command == "stop":
            runner.stop_all()
        
        elif command == "status":
            check_status()
        
        elif command == "help":
            show_help()
        
        else:
            runner.print_error(f"Unknown command: {command}")
            show_help()
    
    except KeyboardInterrupt:
        runner.stop_all()
    except Exception as e:
        runner.print_error(f"Error: {e}")
        runner.stop_all()

if __name__ == "__main__":
    main()
