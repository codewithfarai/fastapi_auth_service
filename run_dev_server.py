# run_dev_server.py
"""
Development server runner with enhanced logging
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings


def main():
    """Run the development server"""
    print("🚀 Starting FastAPI Development Server")
    print("=" * 50)
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")
    print("=" * 50)
    print("📍 Available endpoints:")
    print("  • Application: http://localhost:8000")
    print("  • Health: http://localhost:8000/health")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • ReDoc: http://localhost:8000/redoc")
    print("=" * 50)
    print("Press CTRL+C to stop the server")
    print()
    
    # Configure uvicorn
    config = {
        "app": "app.main:app",
        "host": settings.host,
        "port": settings.port,
        "reload": settings.environment == "development",
        "log_level": "debug" if settings.debug else "info",
        "access_log": True,
        "reload_dirs": ["app"] if settings.environment == "development" else None
    }
    
    # Start server
    uvicorn.run(**config)


if __name__ == "__main__":
    main()