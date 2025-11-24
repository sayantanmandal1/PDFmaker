#!/usr/bin/env python3
"""
Backend startup script for AI Document Generator API.
"""
import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def setup_environment():
    """Set up environment variables and configuration."""
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed
    
    # Set default environment variables if not already set
    env_defaults = {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "INFO",
        "LOG_TO_FILE": "false",
        "ALLOWED_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "RELOAD": "true",
        "DEBUG": "false"
    }
    
    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = default_value

def validate_environment():
    """Validate required environment variables."""
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or environment configuration.")
        sys.exit(1)

def main():
    """Main startup function."""
    print("🚀 Starting AI Document Generator API...")
    
    # Setup environment
    setup_environment()
    
    # Validate environment
    validate_environment()
    
    # Import settings after environment is set up
    from config import settings
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(f"📊 Environment: {settings.environment}")
    print(f"🌐 Host: {settings.host}")
    print(f"🔌 Port: {settings.port}")
    print(f"🔄 Reload: {settings.reload}")
    print(f"📝 Log Level: {settings.log_level}")
    print(f"🔧 Debug Mode: {settings.debug}")
    
    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()