#!/usr/bin/env python3
"""
Start the Apex Wealth server on port 8000
"""
import uvicorn
import os

# Change to the directory containing this script so imports work correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

if __name__ == "__main__":
    print("🚀 Starting Apex Wealth server...")
    print("📍 Landing page: http://localhost:8000")
    print("💬 Chat interface: http://localhost:8000/ui")
    print("📊 API docs: http://localhost:8000/docs")
    print("🔧 Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    # Use import string format for reload to work properly
    # This allows uvicorn to watch for file changes and auto-reload
    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1", 
        port=8000, 
        log_level="info",
        reload=True
    )
