#!/usr/bin/env python3
"""
Quick start script to set up and run TB Coin Engine ML
"""
import os
import sys
import subprocess


def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        if os.path.exists('.env.example'):
            subprocess.run(['cp', '.env.example', '.env'])
            print("✅ Created .env from .env.example")
            print("⚠️  Please edit .env and add your OPENAI_API_KEY if you want to use LLM features")
        else:
            print("⚠️  .env.example not found")
    else:
        print("✅ .env file already exists")


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def run_server():
    """Run the FastAPI server"""
    print("\n🚀 Starting TB Coin Engine ML server...")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")


def main():
    """Main setup and run function"""
    print("=" * 60)
    print("TB Coin Engine ML - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Run server
    run_server()


if __name__ == "__main__":
    main()
