from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.rag_routes import rag_router as rag_router
from app.api.chroma_routes import chroma_router as chroma_router
from app.core.config import get_settings
from app.core.middleware import validate_api_key
from app.services.document_loader import document_loader
from app.services.chroma_service import chroma_service
from app.services.embedding_service import embedding_service
from app.utils.logger import api_logger
import os
from contextlib import asynccontextmanager
import uvicorn
import socket
import sys

settings = get_settings()

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    Processes all txt files in data/raw directory on startup.
    """
    try:
        # Initialize ChromaDB
        chroma_service.initialize(embedding_service.embeddings)

        # Ensure data/raw directory exists
        raw_dir = os.path.join("data", "raw")
        
        if not os.path.exists(raw_dir):
            os.makedirs(raw_dir)
            api_logger.info(f"Created directory: {raw_dir}")

        else:
            # Process all txt files
            stats = document_loader.process_directory(raw_dir, chroma_service)
            api_logger.info(f"Startup processing complete. Stats: {stats}")

    except Exception as e:
        api_logger.error(f"Error during startup processing: {str(e)}")
    
    yield  # This is where the application runs
    
    # Cleanup code (if needed) would go here

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

# Include routers
app.include_router(rag_router)
app.include_router(chroma_router)

if __name__ == "__main__":
    try:
        # Check if port is in use
        if is_port_in_use(settings.API_PORT):
            api_logger.error(f"Port {settings.API_PORT} is already in use. Please ensure no other instance of the server is running.")
            sys.exit(1)

        api_logger.info("Starting RAG Chat API server...")
        uvicorn.run(
            "main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=False
        )
    except Exception as e:
        api_logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1) 