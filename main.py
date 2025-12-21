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
from pathlib import Path

# Add the project root directory to Python path (same as Flask wsgi.py)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

# Setup logging
from infrastructure.logging import setup_logging, get_logger
from infrastructure.config.settings import settings

# Configure logging at startup
log_file = Path(settings.log_file) if settings.log_file else None
setup_logging(
    level=settings.log_level,
    log_file=log_file,
    enable_file=bool(log_file)
)

logger = get_logger(__name__)

# Create FastAPI application (equivalent to Flask's create_app())
app = FastAPI(
    title="League Analyzer API",
    description="Bowling league statistics and analytics API",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("League Analyzer API starting up")
    logger.info(f"Log level: {settings.log_level}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("League Analyzer API shutting down")

# Mount static files from legacy v1 app (same as Flask)
static_path = Path(__file__).parent / "league_analyzer_v1" / "app" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates from legacy v1 app (same as Flask)
templates_path = Path(__file__).parent / "league_analyzer_v1" / "app" / "templates"
jinja_env = None
if templates_path.exists():
    jinja_env = Environment(loader=FileSystemLoader(str(templates_path)))

# Hello World Example
@app.get("/")
def hello_world():
    """Hello World endpoint - equivalent to Flask's index route"""
    logger.info("Hello World endpoint accessed")
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

# Vue.js test page
@app.get("/vue-test", response_class=HTMLResponse)
def vue_test_page(request: Request):
    """Vue.js table test page"""
    if jinja_env:
        template = jinja_env.get_template("vue_test.html")
        return HTMLResponse(content=template.render())
    return HTMLResponse(content="<h1>Templates directory not found</h1>")

# Test table data endpoint
@app.get("/api/v1/test-table")
def test_table_data():
    """Test endpoint that returns sample table data for Vue.js"""
    return {
        "title": "Sample League Standings",
        "columns": [
            {"field": "position", "title": "Position", "decimal_places": 0},
            {"field": "team", "title": "Team"},
            {"field": "points", "title": "Points", "decimal_places": 0},
            {"field": "score", "title": "Score", "decimal_places": 0},
            {"field": "average", "title": "Average", "decimal_places": 2},
            {"field": "games", "title": "Games", "decimal_places": 0}
        ],
        "data": [
            {"position": 1, "team": "Team Alpha", "points": 45, "score": 1250, "average": 208.33, "games": 6},
            {"position": 2, "team": "Team Beta", "points": 42, "score": 1220, "average": 203.33, "games": 6},
            {"position": 3, "team": "Team Gamma", "points": 38, "score": 1180, "average": 196.67, "games": 6},
            {"position": 4, "team": "Team Delta", "points": 35, "score": 1150, "average": 191.67, "games": 6},
            {"position": 5, "team": "Team Epsilon", "points": 32, "score": 1120, "average": 186.67, "games": 6}
        ]
    }

# ============================================================================
# TEMPORARY DEMO ROUTES - CAN BE REMOVED AFTER PHASE 1
# ============================================================================
# These routes demonstrate domain services working with test data.
# TODO: Remove when Phase 2 (Application Layer) is implemented.
from presentation.api.temp_demo_routes import router as temp_demo_router
app.include_router(temp_demo_router)

# Import sample_data_routes - register BEFORE other routes to ensure it's included
try:
    from presentation.api.sample_data_routes import router as sample_data_router
    app.include_router(sample_data_router)
    logger.info(f"Sample data router registered: {len(sample_data_router.routes)} routes")
    logger.info(f"Sample data router prefix: {sample_data_router.prefix}")
    logger.info(f"Sample data router tags: {sample_data_router.tags}")
except Exception as e:
    logger.error(f"FAILED to register sample_data_router: {e}", exc_info=True)
    raise

# Demo page route
@app.get("/demo", response_class=HTMLResponse)
def demo_page(request: Request):
    """TEMPORARY: Demo page showing domain services in action"""
    if jinja_env:
        template = jinja_env.get_template("demo.html")
        return HTMLResponse(content=template.render())
    return HTMLResponse(content="<h1>Templates directory not found</h1>")

# Demo links page route
@app.get("/demo-links", response_class=HTMLResponse)
def demo_links_page(request: Request):
    """TEMPORARY: Page with all demo endpoint links"""
    if jinja_env:
        template = jinja_env.get_template("demo_links.html")
        return HTMLResponse(content=template.render())
    return HTMLResponse(content="<h1>Templates directory not found</h1>")

# Run development server (equivalent to Flask's app.run(debug=True))
if __name__ == '__main__':
    import uvicorn
    
    # Log all registered routes at startup
    logger.info("=" * 60)
    logger.info("REGISTERED ROUTES:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', set())
            methods_str = ', '.join(sorted(methods)) if methods else 'N/A'
            logger.info(f"  {route.path:50} [{methods_str}]")
    logger.info("=" * 60)
    
    # Run with auto-reload (same as Flask's debug=True)
    uvicorn.run(
        "main:app",  # Import path to FastAPI app
        host="127.0.0.1",
        port=5000,  # Same port as Flask
        reload=True,  # Auto-reload on code changes (like Flask's debug=True)
        reload_dirs=["./app", "./domain", "./application", "./presentation"],  # Watch these directories
        log_level="info"
    )

