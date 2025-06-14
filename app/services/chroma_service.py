from typing import List, Dict, Optional
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain.schema.retriever import BaseRetriever
from app.core.interfaces import IVectorStore, IConfiguration, IEmbeddingModel
from app.core.base_service import BaseService
from app.utils.logger import api_logger
import os
import hashlib
import json

class ChromaService(BaseService, IVectorStore):
    """Service for handling vector store operations using ChromaDB"""
    _instance = None
    
    def __new__(cls, config: IConfiguration, embedding_model: IEmbeddingModel):
        if cls._instance is None:
            cls._instance = super(ChromaService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: IConfiguration, embedding_model: IEmbeddingModel):
        if not hasattr(self, 'initialized'):
            super().__init__(config, "chroma_service")
            self._embedding_model = embedding_model
            self._vector_store = None
            self._persist_directory = os.path.join("data", "chroma")
    
    def _initialize(self) -> None:
        """Initialize the vector store"""
        try:
            self.logger.info("Initializing ChromaDB")
            self._vector_store = Chroma(
                persist_directory=self._persist_directory,
                embedding_function=self._embedding_model.model
            )
            self.logger.info("Successfully initialized ChromaDB")
        except Exception as e:
            self.logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def _shutdown(self) -> None:
        """Clean up resources"""
        self._vector_store = None
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        self._vector_store.add_documents(documents)
        self._vector_store.persist()
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        return self._vector_store.similarity_search(query, k=k)
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents from the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        return self._vector_store.get()
    
    def delete_document(self, document_id: str) -> None:
        """Delete a document from the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        self._vector_store.delete([document_id])
        self._vector_store.persist()
    
    def delete_all(self) -> None:
        """Delete all documents from the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        self._vector_store.delete_collection()
        self._vector_store = Chroma(
            persist_directory=self._persist_directory,
            embedding_function=self._embedding_model.model
        )
    
    def sync_directory(self, directory: str) -> None:
        """Sync documents from a directory to the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        if not os.path.exists(directory):
            self.logger.warning(f"Directory {directory} does not exist")
            return
            
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                if not self.is_file_processed(file_path):
                    self.logger.info(f"Processing new file: {filename}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        doc = Document(
                            page_content=content,
                            metadata={
                                'source': file_path,
                                'filename': filename
                            }
                        )
                        self.add_documents([doc])
                else:
                    self.logger.info(f"File already processed: {filename}")
    
    def is_file_processed(self, file_path: str) -> bool:
        """Check if a file has been processed"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        file_hash = self._get_file_hash(file_path)
        existing_docs = self._vector_store.get(
            where={"source": file_path}
        )
        return len(existing_docs) > 0
    
    def get_file_documents(self, file_path: str) -> List[Document]:
        """Get all documents associated with a file"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        return self._vector_store.get(
            where={"source": file_path}
        )
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get the hash of a file"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _should_update_document(self, doc: Document, file_path: str) -> bool:
        """Check if a document should be updated"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        existing_docs = self._vector_store.get(
            where={"source": file_path}
        )
        if not existing_docs:
            return True
            
        return self._get_file_hash(file_path) != existing_docs[0].metadata.get('hash')
    
    def as_retriever(self, **kwargs) -> BaseRetriever:
        """Get a retriever interface for the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        return self._vector_store.as_retriever(**kwargs)
    
    @property
    def vector_store(self) -> Chroma:
        """Get the vector store instance"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        return self._vector_store
