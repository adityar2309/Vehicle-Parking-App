#!/usr/bin/env python3
"""
Setup Script for Vehicle Parking App Backend - MongoDB Version

This script helps set up the backend with MongoDB and simplified architecture.
Redis and Celery dependencies have been removed.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n[{step}] {description}")

def check_command(command):
    """Check if a command is available"""
    return shutil.which(command) is not None

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def setup_environment():
    """Set up the environment"""
    print_header("Environment Setup")
    
    # Check Python version
    print_step("1", "Checking Python version")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check required commands
    print_step("2", "Checking required commands")
    required_commands = ['pip', 'mongod']  # Changed from redis-server to mongod
    optional_commands = ['mongo', 'mongosh']  # MongoDB client commands
    missing_commands = []
    
    for cmd in required_commands:
        if check_command(cmd):
            print(f"✅ {cmd} is available")
        else:
            print(f"❌ {cmd} is not available")
            missing_commands.append(cmd)
    
    # Check optional MongoDB client
    mongo_client_available = False
    for cmd in optional_commands:
        if check_command(cmd):
            print(f"✅ {cmd} is available")
            mongo_client_available = True
            break
    
    if not mongo_client_available:
        print("⚠️  MongoDB client (mongo/mongosh) not found - optional but recommended")
    
    if missing_commands:
        print(f"\nMissing commands: {', '.join(missing_commands)}")
        print("Please install the missing dependencies:")
        print("- MongoDB: https://docs.mongodb.com/manual/installation/")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    print_step("1", "Upgrading pip")
    if not run_command("pip install --upgrade pip", "Pip upgrade"):
        return False
    
    print_step("2", "Installing requirements")
    if not run_command("pip install -r requirements.txt", "Requirements installation"):
        return False
    
    return True

def setup_configuration():
    """Set up configuration files"""
    print_header("Configuration Setup")
    
    print_step("1", "Creating environment file")
    env_example = Path("env_example.txt")
    env_file = Path(".env")
    
    if env_example.exists():
        if not env_file.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual configuration")
        else:
            print("✅ .env file already exists")
    else:
        print("❌ env_example.txt not found")
        return False
    
    print_step("2", "Creating temp directories")
    temp_dir = Path("temp_files")
    temp_dir.mkdir(exist_ok=True)
    print("✅ Created temp_files directory")
    
    return True

def test_mongodb():
    """Test MongoDB connection"""
    print_header("Testing MongoDB")
    
    print_step("1", "Checking MongoDB server")
    # Try to connect to MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()  # Will raise exception if can't connect
        print("✅ MongoDB is running and accessible")
        client.close()
        return True
    except Exception as e:
        print("❌ MongoDB is not accessible")
        print(f"Error: {str(e)}")
        print("Please start MongoDB server:")
        print("  mongod")
        return False

def initialize_database():
    """Initialize the database"""
    print_header("Database Initialization")
    
    print_step("1", "Creating MongoDB collections and sample data")
    try:
        from app import create_app, init_database
        app = create_app()
        init_database(app)
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_services():
    """Test all services"""
    print_header("Testing Services")
    
    print_step("1", "Testing Flask app")
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False
    
    print_step("2", "Testing cache service")
    try:
        from cache_service import CacheService
        print("✅ Cache service imported successfully (using simple in-memory cache)")
    except Exception as e:
        print(f"❌ Cache service test failed: {e}")
        return False
    
    print_step("3", "Testing email service")
    try:
        from email_service import EmailService
        print("✅ Email service imported successfully")
    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        return False
    
    print_step("4", "Testing background jobs")
    try:
        from background_jobs import daily_reminder_job
        print("✅ Background jobs imported successfully (synchronous execution)")
    except Exception as e:
        print(f"❌ Background jobs test failed: {e}")
        return False
    
    print_step("5", "Testing MongoDB models")
    try:
        from models import User, ParkingLot, ParkingSpot, Reservation
        print("✅ MongoDB models imported successfully")
    except Exception as e:
        print(f"❌ MongoDB models test failed: {e}")
        return False
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print_header("Setup Complete!")
    
    print("\n🎉 Backend setup completed successfully!")
    print("\nNext steps:")
    print("\n1. Configure your environment:")
    print("   - Edit .env file with your actual settings")
    print("   - Set up email SMTP credentials")
    print("   - Configure MongoDB URI if using remote MongoDB")
    
    print("\n2. Start the services:")
    print("   Terminal 1: mongod (if not running as service)")
    print("   Terminal 2: python app.py")
    
    print("\n3. Test the application:")
    print("   - Visit http://localhost:5000")
    print("   - Login with admin/admin123")
    print("   - Test CSV export functionality")
    
    print("\n4. Architecture changes:")
    print("   - ✅ MongoDB replaces PostgreSQL")
    print("   - ✅ Simple in-memory cache replaces Redis")
    print("   - ✅ Synchronous jobs replace Celery")
    print("   - ✅ No Redis dependencies")
    print("   - ✅ Simplified deployment")
    
    print("\n📚 Documentation:")
    print("   - BACKEND_FEATURES.md - Complete feature documentation")
    print("   - env_example.txt - Configuration reference")
    
    print("\n🔧 Troubleshooting:")
    print("   - Check MongoDB: mongod --version")
    print("   - Check connection: mongo or mongosh")
    print("   - Verify .env configuration")

def main():
    """Main setup function"""
    print_header("Vehicle Parking App - Backend Setup (MongoDB)")
    print("This script will set up the backend with MongoDB and simplified architecture.")
    print("Redis and Celery dependencies have been removed.")
    
    # Run setup steps
    steps = [
        ("Environment Check", setup_environment),
        ("Install Dependencies", install_dependencies),
        ("Configuration Setup", setup_configuration),
        ("MongoDB Test", test_mongodb),
        ("Database Initialization", initialize_database),
        ("Service Tests", test_services),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the issues and run the setup again.")
            sys.exit(1)
    
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1) 