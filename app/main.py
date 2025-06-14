import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.core.application import Application
from app.core.config import Configuration
from app.core.middleware import validate_api_key
from app.utils.check_ports import is_port_in_use
from app.utils.logger import api_logger
import uvicorn
import sys

# Get configuration
config = Configuration()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI application"""
    try:
        # Ensure data directory exists
        raw_dir = os.path.join("data", "raw")
        if not os.path.exists(raw_dir):
            os.makedirs(raw_dir)
            api_logger.info(f"Created directory: {raw_dir}")
        
        # Initialize application services
        app_instance = Application.get_instance()
        app_instance.initialize_services()
        
        # Sync documents from raw directory
        app_instance.chroma_service.sync_directory(raw_dir)
        
        api_logger.info("Application startup complete")
        yield
    except Exception as e:
        api_logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        try:
            app_instance = Application.get_instance()
            app_instance.shutdown_services()
            api_logger.info("Application shutdown complete")
        except Exception as e:
            api_logger.error(f"Error during shutdown: {str(e)}")
            raise

# Create FastAPI app
app = FastAPI(
    title="LDC Technical Assessment",
    description="RAG Chatbot System API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7000", "http://127.0.0.1:7000", "localhost:7000", "127.0.0.1:7000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type", "Accept"],
    expose_headers=["*"],
    max_age=3600,
)

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Middleware to validate API key and origin for all requests"""
    api_logger.info(f"Processing request: {request.method} {request.url.path}")
    api_logger.info(f"Request headers: {dict(request.headers)}")
    
    # Validate API key and origin
    validation_response = await validate_api_key(request)
    if validation_response is not None:
        return validation_response

    # If validation passes, proceed with the request
    response = await call_next(request)
    return response

# Add API router
app.include_router(router)

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