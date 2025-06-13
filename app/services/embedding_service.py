from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from app.core.config import settings
from app.services.db_service import db_service
from app.utils.logger import embedding_logger



class EmbeddingService:
    _instance = None
    _embeddings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            embedding_logger.info("Creating new EmbeddingService instance")
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            embedding_logger.info("Initializing EmbeddingService")
            self._initialize_embeddings()
            self.initialized = True

    def _initialize_embeddings(self):
        """Initialize the embeddings model"""
        if self._embeddings is None:
            embedding_logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL_NAME
                )
                embedding_logger.info("Successfully loaded embeddings model")
                
                # Initialize database service with embeddings
                if not db_service.is_initialized():
                    db_service.initialize(self._embeddings)
            except Exception as e:
                embedding_logger.error(f"Error loading embeddings model: {str(e)}")
                raise

    @property
    def embeddings(self):
        return self._embeddings

    @property
    def vector_store(self):
        return db_service.vector_store

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
            db_service.initialize(self.embeddings)
            
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

embedding_service = EmbeddingService()
