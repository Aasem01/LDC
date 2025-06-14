from fastapi import APIRouter
from app.api.chroma_routes import chroma_router
from app.api.rag_routes import rag_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(chroma_router)
router.include_router(rag_router) 