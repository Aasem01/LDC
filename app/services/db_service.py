from langchain_chroma import Chroma
from app.core.config import settings
from app.utils.logger import chroma_logger
from typing import Optional


class DatabaseService:
    _instance = None
    _vector_store = None
    _embeddings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            chroma_logger.info("Creating new DatabaseService instance")
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            chroma_logger.info("Initializing DatabaseService")
            self.initialized = True

    def initialize(self, embeddings):
        """Initialize the ChromaDB connection with embeddings"""
        try:
            if self._vector_store is None:
                chroma_logger.info("Initializing ChromaDB connection")
                self._embeddings = embeddings
                self._vector_store = Chroma(
                    persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                    embedding_function=embeddings
                )
                chroma_logger.info("ChromaDB connection initialized successfully")
            return self._vector_store
        except Exception as e:
            chroma_logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise

    def is_initialized(self) -> bool:
        """Check if the vector store is initialized"""
        return self._vector_store is not None

    @property
    def vector_store(self) -> Optional[Chroma]:
        """Get the vector store instance"""
        if self._vector_store is None:
            chroma_logger.warning("Vector store not initialized")
            return None
        return self._vector_store

    def get_vector_store(self) -> Chroma:
        """Get the vector store instance, raising an error if not initialized"""
        if self._vector_store is None:
            raise ValueError("Vector store not initialized. Please initialize the database service first.")
        return self._vector_store

# Create singleton instance
db_service = DatabaseService() 