#!/usr/bin/env python3
"""
MongoDB setup and installation guide
"""

import os
import subprocess
import sys
import platform

def check_docker_available():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_docker_compose_available():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_mongodb_docker_running():
    """Check if MongoDB Docker container is running"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=dvc-ai-mongodb', '--format', '{{.Names}}'], 
                              capture_output=True, text=True, timeout=10)
        return 'dvc-ai-mongodb' in result.stdout
    except:
        return False

def start_mongodb_docker():
    """Start MongoDB using Docker Compose"""
    try:
        result = subprocess.run(['docker-compose', '-f', 'docker-compose-mongodb.yml', 'up', '-d'], 
                              capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def stop_mongodb_docker():
    """Stop MongoDB using Docker Compose"""
    try:
        result = subprocess.run(['docker-compose', '-f', 'docker-compose-mongodb.yml', 'down'], 
                              capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_mongodb_installed():
    """Check if MongoDB is installed"""
    try:
        result = subprocess.run(['mongod', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_mongodb_running():
    """Check if MongoDB is running"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
        return True
    except:
        return False

def install_mongodb_windows():
    """Guide for installing MongoDB on Windows"""
    print("📋 MongoDB Installation Guide for Windows:")
    print("1. Download MongoDB Community Server from:")
    print("   https://www.mongodb.com/try/download/community")
    print("2. Run the installer (.msi file)")
    print("3. Choose 'Complete' installation")
    print("4. Check 'Install MongoDB as a Service'")
    print("5. Check 'Install MongoDB Compass' (optional GUI)")
    print("6. After installation, MongoDB should start automatically as a service")
    print("\nAlternatively, using chocolatey:")
    print("   choco install mongodb")

def install_mongodb_mac():
    """Guide for installing MongoDB on macOS"""
    print("📋 MongoDB Installation Guide for macOS:")
    print("Using Homebrew:")
    print("1. brew tap mongodb/brew")
    print("2. brew install mongodb-community")
    print("3. brew services start mongodb/brew/mongodb-community")

def install_mongodb_linux():
    """Guide for installing MongoDB on Linux"""
    print("📋 MongoDB Installation Guide for Linux:")
    print("Ubuntu/Debian:")
    print("1. sudo apt-get update")
    print("2. sudo apt-get install -y mongodb")
    print("3. sudo systemctl start mongodb")
    print("4. sudo systemctl enable mongodb")
    print("\nCentOS/RHEL:")
    print("1. sudo yum install -y mongodb-org")
    print("2. sudo systemctl start mongod")
    print("3. sudo systemctl enable mongod")

def start_mongodb_windows():
    """Start MongoDB on Windows"""
    try:
        # Try to start MongoDB service
        result = subprocess.run(['net', 'start', 'MongoDB'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB service started successfully")
            return True
        else:
            print("⚠️ Could not start MongoDB service")
            print("Try running as Administrator or start manually:")
            print("   net start MongoDB")
            return False
    except Exception as e:
        print(f"❌ Error starting MongoDB: {e}")
        return False

def main():
    print("=== MongoDB Setup for DVC.AI ===\n")
    
    # Check Docker availability
    print("1. 🔍 Checking Docker status...")
    docker_available = check_docker_available()
    docker_compose_available = check_docker_compose_available()
    mongodb_docker_running = check_mongodb_docker_running()
    
    print(f"   Docker Available: {'✅' if docker_available else '❌'}")
    print(f"   Docker Compose Available: {'✅' if docker_compose_available else '❌'}")
    print(f"   MongoDB Docker Container: {'✅ Running' if mongodb_docker_running else '❌ Not running'}")
    
    # Check native MongoDB
    print("\n2. 🔍 Checking native MongoDB status...")
    mongodb_installed = check_mongodb_installed()
    mongodb_running = check_mongodb_running()
    
    print(f"   MongoDB Installed: {'✅' if mongodb_installed else '❌'}")
    print(f"   MongoDB Running: {'✅' if mongodb_running else '❌'}")
    
    # Determine best option
    if mongodb_running:
        print("\n🎉 MongoDB is ready to use!")
        print("✅ Your application will automatically use MongoDB for document storage.")
        if mongodb_docker_running:
            print("📍 Using Docker MongoDB")
            print("🌐 Mongo Express Admin: http://localhost:8081 (admin/admin123)")
        else:
            print("📍 Using native MongoDB installation")
        return
    
    # Recommend Docker first if available
    if docker_available and docker_compose_available:
        print("\n🐳 Docker is available - Recommended approach!")
        
        user_input = input("\n❓ Start MongoDB with Docker? (y/n): ").lower().strip()
        if user_input in ['y', 'yes', '']:
            print("\n🚀 Starting MongoDB with Docker...")
            
            success, stdout, stderr = start_mongodb_docker()
            
            if success:
                print("✅ MongoDB Docker containers started successfully!")
                print("📍 MongoDB: localhost:27017")
                print("🌐 Mongo Express Admin: http://localhost:8081")
                print("👤 Admin credentials: admin/admin123")
                
                # Wait a moment and test connection
                import time
                print("\n⏳ Waiting for MongoDB to be ready...")
                time.sleep(5)
                
                if check_mongodb_running():
                    print("✅ MongoDB connection successful!")
                else:
                    print("⚠️ MongoDB containers started but connection not ready yet")
                    print("   Wait a few more seconds and test again")
            else:
                print(f"❌ Failed to start MongoDB Docker containers")
                print(f"Error: {stderr}")
                print("\n💡 Try running manually:")
                print("   docker-compose -f docker-compose-mongodb.yml up -d")
        else:
            print("❌ Skipping Docker setup")
    
    elif not mongodb_installed:
        print("\n📦 MongoDB is not installed and Docker is not available.")
        system = platform.system().lower()
        
        print("\n🐳 Option 1: Install Docker (Recommended)")
        print("   Download Docker Desktop from: https://www.docker.com/products/docker-desktop")
        print("   Then run this script again")
        
        print("\n💻 Option 2: Install MongoDB natively")
        if 'windows' in system:
            install_mongodb_windows()
        elif 'darwin' in system:
            install_mongodb_mac()
        elif 'linux' in system:
            install_mongodb_linux()
        else:
            print("Please install MongoDB manually for your operating system")
            print("Visit: https://docs.mongodb.com/manual/installation/")
    
    else:
        print("\n🔧 MongoDB is installed but not running.")
        
        if platform.system().lower() == 'windows':
            print("Trying to start MongoDB service...")
            start_mongodb_windows()
        else:
            print("Try starting MongoDB:")
            print("   sudo systemctl start mongodb  # Linux")
            print("   brew services start mongodb-community  # macOS")
    
    print("\n🔧 MongoDB Management Commands:")
    if docker_available and docker_compose_available:
        print("   Start:  docker-compose -f docker-compose-mongodb.yml up -d")
        print("   Stop:   docker-compose -f docker-compose-mongodb.yml down")
        print("   Logs:   docker-compose -f docker-compose-mongodb.yml logs mongodb")
        print("   Reset:  docker-compose -f docker-compose-mongodb.yml down -v")
    
    print("\n📋 After MongoDB is running:")
    print("1. Test connection: python -c \"from database import get_database_status; print(get_database_status())\"")
    print("2. Start your application: python main.py")
    print("3. MongoDB will be used automatically for document storage")
    
    print("\n💡 Note:")
    print("- If MongoDB is not available, the app will use fallback in-memory storage")
    print("- This ensures your application works even without MongoDB")
    print("- For production, MongoDB is recommended for data persistence")

if __name__ == "__main__":
    main()
