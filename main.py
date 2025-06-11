from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.rag_routes import rag_router as rag_router
from app.api.chroma_routes import chroma_router as chroma_router
from app.core.config import get_settings
from app.services.document_loader import document_loader
from app.services.chroma_service import chroma_service
from app.services.embedding_service import embedding_service
from app.utils.logger import api_logger
import os
from contextlib import asynccontextmanager

settings = get_settings()

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rag_router)
app.include_router(chroma_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
     host=settings.API_HOST,
     port=settings.API_PORT) 