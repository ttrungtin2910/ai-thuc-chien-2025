#!/usr/bin/env python3
"""
Docker services setup script
Manages Docker-based dependencies (MongoDB, Redis, Milvus)
"""

import subprocess
import sys
import os
import time
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


class DockerSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent  # Go up to project root
        self.is_windows = platform.system().lower() == 'windows'
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(Colors.colored(f"🐳 {title}", Colors.BOLD + Colors.CYAN))
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
                
                # Stream output
                for line in process.stdout:
                    print(f"[{Colors.colored(name, Colors.BOLD)}] {line.rstrip()}")
                        
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

    def check_docker_compose(self):
        """Check Docker Compose availability"""
        # Try Docker Compose v2 first
        try:
            result = self.run_command(["docker", "compose", "version"], "docker-compose", capture_output=True, timeout=5, check=False)
            if result and result.returncode == 0:
                return "docker compose"
        except:
            pass
        
        # Try Docker Compose v1
        try:
            result = self.run_command(["docker-compose", "--version"], "docker-compose", capture_output=True, timeout=5, check=False)
            if result and result.returncode == 0:
                return "docker-compose"
        except:
            pass
        
        return False
    
    def start_redis(self):
        """Start Redis with Docker"""
        self.print_step("Starting Redis with Docker...")
        
        # Check if already running
        if self.check_redis_connection():
            self.print_success("Redis is already running")
            return True
        
        # Check Docker Compose
        compose_cmd = self.check_docker_compose()
        if not compose_cmd:
            self.print_error("Docker Compose not found")
            return False
            
        # Start Redis container
        try:
            os.chdir(self.project_root)
            
            if compose_cmd == "docker compose":
                cmd = ["docker", "compose", "up", "-d", "redis"]
            else:
                cmd = ["docker-compose", "up", "-d", "redis"]
            
            result = self.run_command(cmd, "Redis Docker", capture_output=True, check=True)
            
            # Wait for Redis to be ready
            self.print_info("Waiting for Redis to start...")
            for i in range(15):
                time.sleep(1)
                if self.check_redis_connection():
                    self.print_success("Redis is ready!")
                    return True
                print(f"   Checking Redis... ({i+1}/15)")
            
            self.print_warning("Redis container started but not responding")
            return False
            
        except Exception as e:
            self.print_error(f"Failed to start Redis: {e}")
            return False

    def start_mongodb(self):
        """Start MongoDB with Docker"""
        self.print_step("Starting MongoDB...")
        
        if self.check_service_running("MongoDB", 27017):
            self.print_success("MongoDB already running")
            return True
        
        # Check Docker Compose
        compose_cmd = self.check_docker_compose()
        if not compose_cmd:
            self.print_error("Docker Compose not found")
            return False
        
        try:
            os.chdir(self.project_root)
            
            if compose_cmd == "docker compose":
                cmd = ["docker", "compose", "up", "-d", "mongodb"]
            else:
                cmd = ["docker-compose", "up", "-d", "mongodb"]
            
            self.run_command(cmd, "MongoDB Docker", capture_output=True)
            
            # Wait for service to be ready
            self.print_info("Waiting for MongoDB to be ready...")
            for i in range(30):
                time.sleep(1)
                if self.check_service_running("MongoDB", 27017):
                    self.print_success("MongoDB is ready!")
                    return True
                print(f"   Waiting... ({i+1}/30)")
            
            self.print_warning("MongoDB started but connection check failed")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to start MongoDB: {e}")
            return False

    def start_milvus(self):
        """Start Milvus with Docker"""
        self.print_step("Starting Milvus...")
        
        if self.check_service_running("Milvus", 19530):
            self.print_success("Milvus already running")
            return True
        
        # Check Docker Compose
        compose_cmd = self.check_docker_compose()
        if not compose_cmd:
            self.print_error("Docker Compose not found")
            return False
        
        try:
            os.chdir(self.project_root)
            
            if compose_cmd == "docker compose":
                cmd = ["docker", "compose", "up", "-d", "milvus", "etcd", "minio", "attu"]
            else:
                cmd = ["docker-compose", "up", "-d", "milvus", "etcd", "minio", "attu"]
            
            self.run_command(cmd, "Milvus Docker", capture_output=True)
            
            # Wait for service to be ready
            self.print_info("Waiting for Milvus to be ready...")
            for i in range(60):
                time.sleep(2)
                if self.check_service_running("Milvus", 19530):
                    self.print_success("Milvus is ready!")
                    return True
                print(f"   Waiting... ({i+1}/60)")
            
            self.print_warning("Milvus started but connection check failed")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to start Milvus: {e}")
            return False

    def fix_mongodb_auth(self):
        """Fix MongoDB authentication issues"""
        self.print_header("MongoDB Authentication Fix")
        
        # Stop MongoDB first
        self.print_step("Stopping MongoDB...")
        compose_cmd = self.check_docker_compose()
        if compose_cmd:
            try:
                os.chdir(self.project_root)
                if compose_cmd == "docker compose":
                    cmd = ["docker", "compose", "stop", "mongodb"]
                else:
                    cmd = ["docker-compose", "stop", "mongodb"]
                self.run_command(cmd, "Stop MongoDB", capture_output=True)
                time.sleep(2)
                
                # Remove the container to reset auth
                self.print_step("Removing MongoDB container to reset...")
                if compose_cmd == "docker compose":
                    cmd = ["docker", "compose", "rm", "-f", "mongodb"]
                else:
                    cmd = ["docker-compose", "rm", "-f", "mongodb"]
                self.run_command(cmd, "Remove MongoDB", capture_output=True)
                time.sleep(1)
                
                # Start fresh
                self.print_step("Starting fresh MongoDB...")
                if self.start_mongodb():
                    self.print_success("MongoDB authentication fixed!")
                    return True
                else:
                    self.print_error("Failed to restart MongoDB")
                    return False
                    
            except Exception as e:
                self.print_error(f"Error fixing MongoDB: {e}")
                return False
        else:
            self.print_error("Docker Compose not found")
            return False
    
    def stop_all(self):
        """Stop all Docker containers"""
        self.print_header("Stopping Docker Services")
        
        # Stop Docker containers
        compose_cmd = self.check_docker_compose()
        if compose_cmd:
            try:
                os.chdir(self.project_root)
                
                if compose_cmd == "docker compose":
                    cmd = ["docker", "compose", "down"]
                else:
                    cmd = ["docker-compose", "down"]
                
                self.run_command(cmd, "Docker Containers", capture_output=True, check=True)
                self.print_success("Docker containers stopped")
            except:
                self.print_warning("Could not stop some Docker containers")
        else:
            self.print_error("Docker Compose not found")
    
    def start_all(self):
        """Start all Docker services"""
        self.print_header("Docker Services Setup")
        
        # 1. Start MongoDB
        if not self.start_mongodb():
            self.print_error("Failed to start MongoDB")
            return False
        
        time.sleep(2)
        
        # 2. Start Redis
        if not self.start_redis():
            self.print_error("Failed to start Redis")
            return False
        
        time.sleep(2)
        
        # 3. Start Milvus (optional)
        milvus_started = self.start_milvus()
        if not milvus_started:
            self.print_warning("Milvus failed to start - continuing without vector search")
        
        self.show_service_info()
        
        self.print_header("Docker Services Ready! 🎉")
        self.print_info("Run 'python scripts/run.py' to start Python services")
        
        return True
    
    def show_service_info(self):
        """Show information about running Docker services"""
        self.print_header("Docker Service Information")
        
        services = [
            ("MongoDB", 27017, "Database", "localhost:27017"),
            ("Redis", 6379, "Cache & Session Storage", "localhost:6379"),
            ("Milvus", 19530, "Vector Database", "localhost:19530"),
            ("Attu", 8080, "Milvus Admin UI", "http://localhost:8080"),
            ("MinIO", 9001, "Object Storage", "http://localhost:9001")
        ]
        
        print(Colors.colored("🐳 Docker Services:", Colors.BOLD + Colors.GREEN))
        for name, port, description, url in services:
            status = "🟢" if self.check_service_running(name, port) else "🔴"
            print(f"  {status} {Colors.colored(name, Colors.BOLD)}: {url}")
            print(f"     {description}")

def show_help():
    """Show help message"""
    setup = DockerSetup()
    setup.print_header("Docker Services Setup Manager")
    
    commands = [
        ("start", "Start all Docker services (MongoDB, Redis, Milvus)"),
        ("stop", "Stop all Docker services"),
        ("mongodb", "Start only MongoDB"),
        ("redis", "Start only Redis"),
        ("milvus", "Start only Milvus"),
        ("fix-mongodb", "Fix MongoDB authentication issues"),
        ("status", "Check Docker service status"),
        ("help", "Show this help message")
    ]
    
    print(Colors.colored("Commands:", Colors.BOLD + Colors.YELLOW))
    for cmd, desc in commands:
        print(f"  {Colors.colored(cmd, Colors.BOLD + Colors.GREEN):<12} {desc}")
    
    print(f"\n{Colors.colored('Examples:', Colors.BOLD + Colors.YELLOW)}")
    examples = [
        ("python scripts/setup.py start", "Start all Docker dependencies"),
        ("python scripts/setup.py mongodb", "Start only MongoDB"),
        ("python scripts/setup.py stop", "Stop all Docker services"),
        ("python scripts/setup.py status", "Check what's running")
    ]
    
    for cmd, desc in examples:
        print(f"  {Colors.colored(cmd, Colors.CYAN):<30} # {desc}")

def check_status():
    """Check status of Docker services"""
    setup = DockerSetup()
    setup.print_header("Docker Service Status Check")
    
    services = [
        ("MongoDB", 27017),
        ("Redis", 6379),
        ("Milvus", 19530),
        ("Attu", 8080),
        ("MinIO", 9001)
    ]
    
    for service_name, port in services:
        if setup.check_service_running(service_name, port):
            setup.print_success(f"{service_name}: Running on port {port}")
        else:
            setup.print_error(f"{service_name}: Not running on port {port}")
    
    # Check Redis connection specifically
    if setup.check_redis_connection():
        setup.print_success("Redis: Connection successful")
    else:
        setup.print_warning("Redis: Port open but connection failed")
    
    # Check MongoDB connection with authentication
    if setup.check_mongodb_connection():
        setup.print_success("MongoDB: Authentication successful")
    else:
        setup.print_warning("MongoDB: Port open but authentication failed")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    setup = DockerSetup()
    
    try:
        if command == "start":
            setup.start_all()
        
        elif command == "stop":
            setup.stop_all()
        
        elif command == "mongodb":
            setup.start_mongodb()
        
        elif command == "redis":
            setup.start_redis()
        
        elif command == "milvus":
            setup.start_milvus()
        
        elif command == "fix-mongodb":
            setup.fix_mongodb_auth()
        
        elif command == "status":
            check_status()
        
        elif command == "help":
            show_help()
        
        else:
            setup.print_error(f"Unknown command: {command}")
            show_help()
    
    except KeyboardInterrupt:
        setup.stop_all()
    except Exception as e:
        setup.print_error(f"Error: {e}")

if __name__ == "__main__":
    main()
