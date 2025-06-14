from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from app.core.config import settings
from app.services.db_service import db_service
from app.utils.logger import embedding_logger, api_logger
from app.core.interfaces import IEmbeddingModel, IConfiguration
from app.core.base_service import BaseService



class EmbeddingService(BaseService, IEmbeddingModel):
    """Service for handling document and query embeddings"""
    _instance = None
    
    def __new__(cls, config: IConfiguration):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: IConfiguration):
        if not hasattr(self, 'initialized'):
            super().__init__(config, "embedding_service")
            self._model = None
    
    def _initialize(self) -> None:
        """Initialize the embedding model"""
        try:
            self.logger.info("Initializing embedding model")
            self._model = HuggingFaceEmbeddings(
                model_name=self.config.settings.HUGGINGFACE_MODEL_NAME,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            self.logger.info("Successfully initialized embedding model")
        except Exception as e:
            self.logger.error(f"Error initializing embedding model: {str(e)}")
            raise
    
    def _shutdown(self) -> None:
        """Clean up resources"""
        self._model = None
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        if not self.is_initialized:
            raise RuntimeError("EmbeddingService not initialized")
        return self._model.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query"""
        if not self.is_initialized:
            raise RuntimeError("EmbeddingService not initialized")
        return self._model.embed_query(text)
    
    @property
    def model(self) -> HuggingFaceEmbeddings:
        """Get the embedding model"""
        if not self.is_initialized:
            raise RuntimeError("EmbeddingService not initialized")
        return self._model

    def create_vector_store(self, documents: List[Document]) -> None:
        """
        Create a vector store from documents.
        
        Args:
            documents (List[Document]): List of documents to create embeddings for
        """
        embedding_logger.info(f"Creating vector store with {len(documents)} documents")
        embedding_logger.debug(f"Persistence directory: {settings.CHROMA_PERSIST_DIRECTORY}")
        
        try:
            # Initialize the database service with embeddings
            db_service.initialize(self.model)
            
            # Add documents to the vector store
            vector_store = db_service.get_vector_store()
            vector_store.add_documents(documents)
            vector_store.persist()
            
            embedding_logger.info("Successfully created and persisted vector store")
        except Exception as e:
            embedding_logger.error(f"Error creating vector store: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query (str): Query string
            k (int): Number of results to return
            
        Returns:
            List[Document]: List of similar documents
        """
        embedding_logger.info(f"Performing similarity search for query: {query}")
        embedding_logger.debug(f"Requesting {k} results")
        
        try:
            vector_store = db_service.get_vector_store()
            results = vector_store.similarity_search(query, k=k)
            embedding_logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            embedding_logger.error(f"Error during similarity search: {str(e)}")
            raise 
