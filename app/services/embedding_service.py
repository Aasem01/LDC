from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from app.core.config import get_settings
from app.utils.logger import embedding_logger

settings = get_settings()

class EmbeddingService:
    _instance = None
    _embeddings = None
    _vector_store = None

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
            except Exception as e:
                embedding_logger.error(f"Error loading embeddings model: {str(e)}")
                raise

    @property
    def embeddings(self):
        return self._embeddings

    @property
    def vector_store(self):
        if self._vector_store is None:
            self.load_vector_store()
        return self._vector_store

    def create_vector_store(self, documents: List[Document]) -> None:
        """
        Create a vector store from documents.
        
        Args:
            documents (List[Document]): List of documents to create embeddings for
        """
        embedding_logger.info(f"Creating vector store with {len(documents)} documents")
        embedding_logger.debug(f"Persistence directory: {settings.CHROMA_PERSIST_DIRECTORY}")
        
        try:
            self._vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            )
            self._vector_store.persist()
            embedding_logger.info("Successfully created and persisted vector store")
        except Exception as e:
            embedding_logger.error(f"Error creating vector store: {str(e)}")
            raise

    def load_vector_store(self) -> None:
        """
        Load an existing vector store from disk.
        """
        embedding_logger.info("Attempting to load existing vector store")
        embedding_logger.debug(f"Loading from: {settings.CHROMA_PERSIST_DIRECTORY}")
        
        try:
            self._vector_store = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                embedding_function=self.embeddings
            )
            embedding_logger.info("Successfully loaded vector store")
        except Exception as e:
            embedding_logger.error(f"Error loading vector store: {str(e)}")
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
        
        if not self.vector_store:
            error_msg = "Vector store not initialized"
            embedding_logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            results = self.vector_store.similarity_search(query, k=k)
            embedding_logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            embedding_logger.error(f"Error during similarity search: {str(e)}")
            raise 


embedding_service = EmbeddingService()
