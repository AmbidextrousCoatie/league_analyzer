"""
FastAPI Application Entry Point
Equivalent to wsgi.py for Flask development

Run with:
    python main.py
    OR
    uvicorn main:app --reload
"""

import sys
import os

# Add the project root directory to Python path (same as Flask wsgi.py)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create FastAPI application (equivalent to Flask's create_app())
app = FastAPI(
    title="League Analyzer API",
    description="Bowling league statistics and analytics API",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Hello World Example
@app.get("/")
def hello_world():
    """Hello World endpoint - equivalent to Flask's index route"""
    return {
        "message": "Hello World! League Analyzer API is running.",
        "status": "ok",
        "framework": "FastAPI",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "league-analyzer-api"
    }

# Example API endpoint
@app.get("/api/v1/test")
def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "API is working!",
        "endpoint": "/api/v1/test",
        "method": "GET"
    }

# Run development server (equivalent to Flask's app.run(debug=True))
if __name__ == '__main__':
    import uvicorn
    
    # Run with auto-reload (same as Flask's debug=True)
    uvicorn.run(
        "main:app",  # Import path to FastAPI app
        host="127.0.0.1",
        port=5000,  # Same port as Flask
        reload=True,  # Auto-reload on code changes (like Flask's debug=True)
        reload_dirs=["./app", "./domain", "./application"],  # Watch these directories
        log_level="info"
    )

