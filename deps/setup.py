#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DVC.AI - Unified Setup Script
============================

Tập lệnh setup tự động cho toàn bộ project DVC.AI
Tích hợp tất cả các chức năng setup: dependencies, services, cấu hình
"""

import os
import sys
import subprocess
import platform
import time
import json
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


class DVCAISetup:
    """Main setup class for DVC.AI project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent  # Go up to actual project root
        self.deps_dir = Path(__file__).parent  # deps directory
        self.is_windows = platform.system().lower() == 'windows'
        
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(Colors.colored(f"🚀 {title}", Colors.BOLD + Colors.CYAN))
        print("="*60)
    
    def print_step(self, step, message):
        """Print formatted step"""
        print(f"\n{Colors.colored(f'{step}.', Colors.BOLD + Colors.BLUE)} {message}")
    
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

    def run_command(self, cmd, shell=False, check=True, capture_output=False, timeout=None):
        """Run shell command with proper error handling"""
        try:
            if isinstance(cmd, str) and not shell:
                cmd = cmd.split()
            
            result = subprocess.run(
                cmd, 
                shell=shell, 
                check=check, 
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.CalledProcessError as e:
            if capture_output:
                return e
            raise e
        except subprocess.TimeoutExpired:
            self.print_error(f"Command timed out: {cmd}")
            return None

    def check_python_version(self):
        """Check Python version compatibility"""
        self.print_step(1, "Checking Python version...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.print_success(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            self.print_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
            return False

    def check_docker(self):
        """Check Docker availability"""
        self.print_step(2, "Checking Docker...")
        
        try:
            result = self.run_command(["docker", "--version"], capture_output=True, timeout=5)
            if result and result.returncode == 0:
                self.print_success(f"Docker found: {result.stdout.strip()}")
                return True
        except:
            pass
        
        self.print_error("Docker not found")
        self.print_info("Install Docker from: https://www.docker.com/products/docker-desktop")
        return False

    def check_docker_compose(self):
        """Check Docker Compose availability"""
        self.print_step(3, "Checking Docker Compose...")
        
        # Try Docker Compose v2 first
        try:
            result = self.run_command(["docker", "compose", "version"], capture_output=True, timeout=5)
            if result and result.returncode == 0:
                self.print_success(f"Docker Compose v2: {result.stdout.strip()}")
                return "docker compose"
        except:
            pass
        
        # Try Docker Compose v1
        try:
            result = self.run_command(["docker-compose", "--version"], capture_output=True, timeout=5)
            if result and result.returncode == 0:
                self.print_success(f"Docker Compose v1: {result.stdout.strip()}")
                return "docker-compose"
        except:
            pass
        
        self.print_error("Docker Compose not found")
        return False

    def install_python_dependencies(self):
        """Install Python dependencies"""
        self.print_step(4, "Installing Python dependencies...")
        
        requirements_file = self.project_root / "be" / "requirements.txt"
        if not requirements_file.exists():
            self.print_error("requirements.txt not found")
            return False
        
        try:
            # Upgrade pip first
            self.print_info("Upgrading pip...")
            self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            
            # Install requirements
            self.print_info("Installing packages from requirements.txt...")
            self.run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            
            self.print_success("Python dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install dependencies: {e}")
            return False

    def setup_environment_file(self):
        """Setup environment configuration file"""
        self.print_step(5, "Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / "be" / "env.example"
        
        if env_file.exists():
            self.print_warning(".env file already exists")
            
            # Check if it contains real API key (potential security issue)
            with open(env_file, 'r') as f:
                content = f.read()
                if content.count('sk-') > 0 and 'your-' not in content:
                    self.print_warning("Found potential real API keys in .env file")
                    backup = self.project_root / ".env.backup"
                    
                    # Create backup
                    with open(backup, 'w') as backup_file:
                        backup_file.write(content)
                    self.print_info(f"Created backup: {backup}")
                    
                    # Replace with template
                    if env_example.exists():
                        with open(env_example, 'r') as f:
                            template_content = f.read()
                        with open(env_file, 'w') as f:
                            f.write(template_content)
                        self.print_success("Replaced .env with template for security")
        
        elif env_example.exists():
            # Copy from example
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            self.print_success("Created .env from template")
        else:
            self.print_error("No .env or env.example found")
            return False
        
        self.print_info("Please update .env file with your actual API keys and configuration")
        return True

    def check_service_running(self, service_name, port):
        """Check if a service is running on specified port"""
        try:
            if self.is_windows:
                result = self.run_command(
                    f"netstat -an | findstr :{port}", 
                    shell=True, 
                    capture_output=True,
                    check=False
                )
            else:
                result = self.run_command(
                    ["nc", "-z", "localhost", str(port)], 
                    capture_output=True,
                    check=False
                )
            
            return result and result.returncode == 0
        except:
            return False

    def start_mongodb(self, compose_cmd):
        """Start MongoDB service"""
        self.print_info("Starting MongoDB...")
        
        if self.check_service_running("MongoDB", 27017):
            self.print_success("MongoDB already running")
            return True
        
        try:
            os.chdir(self.project_root)
            
            if compose_cmd == "docker compose":
                cmd = ["docker", "compose", "up", "-d", "mongodb"]
            else:
                cmd = ["docker-compose", "up", "-d", "mongodb"]
            
            self.run_command(cmd)
            
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

    def start_redis(self, compose_cmd):
        """Start Redis service"""
        self.print_info("Starting Redis...")
        
        if self.check_service_running("Redis", 6379):
            self.print_success("Redis already running")
            return True
        
        try:
            os.chdir(self.project_root)
            
            if compose_cmd == "docker compose":
                cmd = ["docker", "compose", "up", "-d", "redis"]
            else:
                cmd = ["docker-compose", "up", "-d", "redis"]
            
            self.run_command(cmd)
            
            # Wait for service to be ready
            self.print_info("Waiting for Redis to be ready...")
            for i in range(15):
                time.sleep(1)
                if self.check_service_running("Redis", 6379):
                    self.print_success("Redis is ready!")
                    return True
                print(f"   Waiting... ({i+1}/15)")
            
            self.print_warning("Redis started but connection check failed")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to start Redis: {e}")
            return False

    def start_milvus(self, compose_cmd):
        """Start Milvus service"""
        self.print_info("Starting Milvus...")
        
        if self.check_service_running("Milvus", 19530):
            self.print_success("Milvus already running")
            return True
        
        try:
            os.chdir(self.project_root)
            
            if compose_cmd == "docker compose":
                cmd = ["docker", "compose", "up", "-d", "milvus", "etcd", "minio", "attu"]
            else:
                cmd = ["docker-compose", "up", "-d", "milvus", "etcd", "minio", "attu"]
            
            self.run_command(cmd)
            
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

    def start_all_services(self):
        """Start all required services"""
        self.print_step(6, "Starting all services...")
        
        # Check Docker first
        if not self.check_docker():
            return False
        
        compose_cmd = self.check_docker_compose()
        if not compose_cmd:
            return False
        
        # Start services
        mongodb_ok = self.start_mongodb(compose_cmd)
        redis_ok = self.start_redis(compose_cmd)
        milvus_ok = self.start_milvus(compose_cmd)
        
        os.chdir(self.project_root)  # Return to project root
        
        if mongodb_ok and redis_ok and milvus_ok:
            self.print_success("All services started successfully!")
            return True
        else:
            self.print_warning("Some services may not have started properly")
            return False

    def show_service_info(self):
        """Show information about running services"""
        self.print_header("Service Information")
        
        services = [
            ("MongoDB", "localhost:27017", "Database"),
            ("Redis", "localhost:6379", "Cache & Session Storage"),
            ("Milvus", "localhost:19530", "Vector Database"),
            ("Attu", "http://localhost:8080", "Milvus Admin UI"),
            ("MinIO", "http://localhost:9001", "Object Storage (minioadmin/minioadmin)")
        ]
        
        for name, url, description in services:
            status = "🟢" if self.check_service_running(name, 
                int(url.split(':')[-1]) if ':' in url and url.split(':')[-1].isdigit() 
                else 8081 if 'Express' in name else 8080 if 'Attu' in name else 9001 if 'MinIO' in name else 0
            ) else "🔴"
            print(f"{status} {Colors.colored(name, Colors.BOLD)}: {url}")
            print(f"   {description}")

    def show_next_steps(self):
        """Show next steps after setup"""
        self.print_header("Next Steps")
        
        steps = [
            ("1. Configure API Keys", "Update .env file with your OpenAI API key"),
            ("2. Load Documents", "python scripts/load_documents_to_milvus.py"),
            ("3. Start Backend", "python main.py"),
            ("4. Start Frontend", "cd ../fe && npm install && npm start")
        ]
        
        for step, command in steps:
            print(f"{Colors.colored(step, Colors.BOLD + Colors.YELLOW)}")
            print(f"   {command}")

    def run_full_setup(self):
        """Run complete setup process"""
        self.print_header("DVC.AI Complete Setup")
        
        # Check requirements
        if not self.check_python_version():
            return False
        
        # Install dependencies
        if not self.install_python_dependencies():
            return False
        
        # Setup environment
        if not self.setup_environment_file():
            return False
        
        # Start services
        if not self.start_all_services():
            return False
        
        # Show results
        self.show_service_info()
        self.show_next_steps()
        
        self.print_header("Setup Complete! 🎉")
        self.print_success("DVC.AI is ready for development!")
        
        return True

    def stop_all_services(self):
        """Stop all services"""
        self.print_header("Stopping All Services")
        
        compose_cmd = self.check_docker_compose()
        if not compose_cmd:
            return False
        
        try:
            os.chdir(self.project_root)
            
            # Stop all services from main compose file
            if compose_cmd == "docker compose":
                cmd = ["docker", "compose", "down"]
            else:
                cmd = ["docker-compose", "down"]
            
            self.run_command(cmd)
            self.print_success("All services stopped!")
            return True
            
        except Exception as e:
            self.print_error(f"Error stopping services: {e}")
            return False

    def show_help(self):
        """Show help information"""
        self.print_header("DVC.AI Setup Help")
        
        commands = [
            ("python setup.py", "Run complete setup"),
            ("python setup.py --help", "Show this help"),
            ("python setup.py --stop", "Stop all services"),
            ("python setup.py --start", "Start services only"),
            ("python setup.py --deps", "Install dependencies only"),
            ("python setup.py --env", "Setup environment only"),
            ("python setup.py --status", "Show service status")
        ]
        
        for cmd, desc in commands:
            print(f"{Colors.colored(cmd, Colors.BOLD + Colors.GREEN)}")
            print(f"   {desc}\n")


def main():
    """Main entry point"""
    setup = DVCAISetup()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            setup.show_help()
        elif arg == '--stop':
            setup.stop_all_services()
        elif arg == '--start':
            setup.start_all_services()
        elif arg == '--deps':
            setup.install_python_dependencies()
        elif arg == '--env':
            setup.setup_environment_file()
        elif arg == '--status':
            setup.show_service_info()
        else:
            print(f"Unknown argument: {arg}")
            setup.show_help()
    else:
        # Run full setup
        setup.run_full_setup()


if __name__ == "__main__":
    main()
