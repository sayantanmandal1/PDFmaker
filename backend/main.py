"""
Main FastAPI application entry point.
"""
import logging
import os
import uuid
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from openai import RateLimitError, APIError, APIConnectionError

from config import settings
from database import engine, Base, get_db
from routers import auth, projects, content
from exceptions import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
    openai_exception_handler,
    general_exception_handler
)

# Configure logging
handlers = [logging.StreamHandler()]
if settings.log_to_file:
    handlers.append(logging.FileHandler('app.log'))

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API for AI-assisted document authoring and generation platform. "
                "Enables users to create, generate, refine, and export structured business documents "
                "(Microsoft Word .docx and PowerPoint .pptx) using Large Language Model assistance.",
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    openapi_url="/openapi.json" if settings.environment != "production" else None,
    contact={
        "name": "AI Document Generator API",
        "url": "https://github.com/your-org/ai-document-generator",
    },
    license_info={
        "name": "MIT",
    },
)

# Add request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add a unique request ID to each request for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log incoming request
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params)
        }
    )
    
    response = await call_next(request)
    
    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} - {response.status_code}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code
        }
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Add exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(RateLimitError, openai_exception_handler)
app.add_exception_handler(APIError, openai_exception_handler)
app.add_exception_handler(APIConnectionError, openai_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📊 Environment: {settings.environment}")
    logger.info(f"🗄️  Database: Connected")
    logger.info(f"📝 Logging level: {settings.log_level}")
    logger.info(f"🌐 CORS Origins: {settings.get_allowed_origins()}")
    
    # Test database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        logger.info("✅ Database connection test successful")
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info(f"👋 Shutting down {settings.app_name}")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(content.router, prefix="/api", tags=["Content"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "AI Document Generator API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint with more detailed information."""
    try:
        # Test database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat() + "Z",
        "components": {
            "database": db_status,
            "api": "healthy"
        },
        "environment": settings.environment
    }

@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "description": "API for AI-assisted document authoring and generation",
        "features": [
            "User authentication and authorization",
            "Project management for Word and PowerPoint documents",
            "AI-powered content generation using OpenAI",
            "Content refinement and feedback system",
            "Document export to .docx and .pptx formats",
            "Template generation for document structures"
        ],
        "endpoints": {
            "authentication": "/api/auth",
            "projects": "/api/projects",
            "content": "/api",
            "health": "/api/health",
            "documentation": "/docs" if settings.environment != "production" else "disabled"
        }
    }
