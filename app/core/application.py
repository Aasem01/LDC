from typing import Optional
from app.core.config import Configuration
from app.core.interfaces import IConfiguration, IVectorStore, IEmbeddingModel, ILLM, IRAGService
from app.utils.logger import api_logger
from app.services.embedding_service import EmbeddingService
from app.services.chroma_service import ChromaService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.document_loader import SimpleTextLoader

class Application:
    """Main application class that manages service lifecycle"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Application, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = api_logger
            self.config = Configuration()
            self._embedding_service: Optional[EmbeddingService] = None
            self._chroma_service: Optional[ChromaService] = None
            self._llm_service: Optional[LLMService] = None
            self._rag_service: Optional[RAGService] = None
            self._document_loader: Optional[SimpleTextLoader] = None
            self.initialized = True
    
    def initialize_services(self) -> None:
        """Initialize all services"""
        try:
            self.logger.info("Initializing services")
            
            # Initialize embedding service
            self._embedding_service = EmbeddingService(self.config)
            self._embedding_service.initialize()
            
            # Initialize LLM service
            self._llm_service = LLMService(self.config)
            self._llm_service.initialize()
            
            # Initialize document loader
            self._document_loader = SimpleTextLoader(self.config)
            self._document_loader.initialize()
            
            # Initialize Chroma service
            self._chroma_service = ChromaService(self.config, self._embedding_service, self._document_loader)
            self._chroma_service.initialize()
            
            # Initialize RAG service
            self._rag_service = RAGService(self.config, self._chroma_service, self._llm_service)
            self._rag_service.initialize()
            
            self.logger.info("All services initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing services: {str(e)}")
            self.shutdown_services()
            raise
    
    def shutdown_services(self) -> None:
        """Shutdown all services"""
        try:
            self.logger.info("Shutting down services")
            
            if self._rag_service:
                self._rag_service.shutdown()
            
            if self._chroma_service:
                self._chroma_service.shutdown()
            
            if self._llm_service:
                self._llm_service.shutdown()
            
            if self._embedding_service:
                self._embedding_service.shutdown()
            
            self.logger.info("All services shut down successfully")
        except Exception as e:
            self.logger.error(f"Error shutting down services: {str(e)}")
            raise
    
    @property
    def embedding_service(self) -> EmbeddingService:
        """Get the embedding service"""
        if not self._embedding_service:
            raise RuntimeError("EmbeddingService not initialized")
        return self._embedding_service
    
    @property
    def chroma_service(self) -> ChromaService:
        """Get the Chroma service"""
        if not self._chroma_service:
            raise RuntimeError("ChromaService not initialized")
        return self._chroma_service
    
    @property
    def llm_service(self) -> LLMService:
        """Get the LLM service"""
        if not self._llm_service:
            raise RuntimeError("LLMService not initialized")
        return self._llm_service
    
    @property
    def rag_service(self) -> RAGService:
        """Get the RAG service"""
        if not self._rag_service:
            raise RuntimeError("RAGService not initialized")
        return self._rag_service
    
    @property
    def document_loader(self) -> SimpleTextLoader:
        """Get the document loader"""
        if not self._document_loader:
            raise RuntimeError("DocumentLoader not initialized")
        return self._document_loader
    
    @classmethod
    def get_instance(cls) -> 'Application':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance 