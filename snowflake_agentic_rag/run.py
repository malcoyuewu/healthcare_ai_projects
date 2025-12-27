#!/usr/bin/env python3
"""
Healthcare Agentic RAG System Launcher
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Please copy .env.template to .env and configure it.")
        return False
    
    # Check required environment variables
    required_vars = [
        # "SNOWFLAKE_ACCOUNT",
        # "SNOWFLAKE_USER", 
        # "SNOWFLAKE_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_streamlit():
    """Start the Streamlit application"""
    print("🎨 Starting Streamlit Healthcare Interface...")
    
    try:
        import subprocess
        import sys
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", str(os.getenv("STREAMLIT_PORT", 8501)),
            "--server.address", os.getenv("STREAMLIT_HOST", "0.0.0.0")
        ])
        
    except ImportError:
        print("❌ Streamlit not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
        run_streamlit()
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")

def run_api():
    """Start the FastAPI server"""
    print("🚀 Starting Healthcare Agentic RAG API...")
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    try:
        import uvicorn
        uvicorn.run(
            "api:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn[standard]"])
        import uvicorn
        uvicorn.run("api:app", host=host, port=port, reload=True)

def run_demo():
    """Run the interactive demo"""
    print("🎯 Starting interactive demo...")
    try:
        from demo import run_demo
        run_demo()
    except ImportError as e:
        print(f"❌ Failed to import demo: {e}")
        sys.exit(1)

def test_api():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    try:
        from demo import test_api_endpoints
        test_api_endpoints()
    except ImportError as e:
        print(f"❌ Failed to import test functions: {e}")
        sys.exit(1)

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description="Healthcare Agentic RAG System")
    parser.add_argument("command", choices=["streamlit", "api", "demo", "test", "setup"], 
                       help="Command to run")
    parser.add_argument("--skip-checks", action="store_true", 
                       help="Skip environment checks")
    
    args = parser.parse_args()
    
    print("🏥 Healthcare Agentic RAG System")
    print("=" * 40)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Environment checks (unless skipped)
    if not args.skip_checks:
        if not check_environment():
            print("\n💡 Run 'python run.py setup' to configure the environment")
            sys.exit(1)
    
    # Execute command
    if args.command == "setup":
        print("🛠️  Setting up environment...")
        
        # Copy template if .env doesn't exist
        if not Path(".env").exists():
            if Path(".env.template").exists():
                import shutil
                shutil.copy(".env.template", ".env")
                print("📋 Copied .env.template to .env")
                print("✏️  Please edit .env file with your configuration")
            else:
                print("❌ .env.template not found")
        
        # Install dependencies
        install_dependencies()
        
        print("\n✅ Setup complete!")
        print("📝 Next steps:")
        print("   1. Edit .env file with your Snowflake credentials")
        print("   2. Run: python run.py streamlit  (Recommended)")
        print("   3. Or run: python run.py demo")
        print("   4. Or run: python run.py api")
        
    elif args.command == "streamlit":
        run_streamlit()
        print("   3. Or run: python run.py api")
        
    elif args.command == "api":
        run_api()
        
    elif args.command == "demo":
        run_demo()
        
    elif args.command == "test":
        test_api()

if __name__ == "__main__":
    main()