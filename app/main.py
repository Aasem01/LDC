import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.rag_routes import rag_router
from app.api.chroma_routes import chroma_router
from app.core.application import Application
from app.core.config import Configuration
from app.core.middleware import validate_api_key
from app.utils.check_ports import is_port_in_use
from app.utils.logger import api_logger
import uvicorn
import sys
from pathlib import Path
import asyncio
from app.core.middleware import validate_api_key


# Get configuration
config = Configuration()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    try:
        # Initialize application
        api_logger.info("Starting the application...")
        app_instance = Application.get_instance()
        
        # Ensure data/raw directory exists
        raw_dir = Path("data/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize services
        app_instance.initialize_services()
        
        # Sync documents from raw directory
        app_instance.chroma_service.sync_directory("data/raw")
        
        # # Debug: Print all documents in Chroma
        api_logger.info("=== Debug: Chroma Database Contents ===")
        all_docs = app_instance.chroma_service.get_all_documents()
        api_logger.info(f"Total documents in Chroma: {len(all_docs)}")
        api_logger.info("Application startup complete")
        yield
    except Exception as e:
        api_logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        # Shutdown services
        api_logger.info("Shutting down services...")
        app_instance.shutdown_services()
        api_logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Configuration().settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API key middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """
    Middleware to validate API key and origin for all requests
    """
    api_logger.info(f"Processing request: {request.method} {request.url.path}")
    api_logger.info(f"Request headers: {dict(request.headers)}")
    
    # Validate API key and origin
    validation_response = await validate_api_key(request)
    if validation_response is not None:
        return validation_response

    # If validation passes, proceed with the request
    response = await call_next(request)
    return response

# Add request logging middleware
app.middleware("http")

# Include API router
app.include_router(rag_router)
app.include_router(chroma_router)


if __name__ == "__main__":
    try:
        # Check if port is in use
        if is_port_in_use(config.settings.API_PORT):
            api_logger.error(f"Port {config.settings.API_PORT} is already in use. Please ensure no other instance of the server is running.")
            sys.exit(1)

        api_logger.info("Starting RAG Chat API server...")
        uvicorn.run(
            "app.main:app",
            host=config.settings.API_HOST,
            port=config.settings.API_PORT,
            reload=False
        )
    except Exception as e:
        api_logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1) 