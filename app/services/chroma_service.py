from typing import List, Dict, Optional, Any
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain.schema.retriever import BaseRetriever
from app.core.interfaces import IVectorStore, IConfiguration, IEmbeddingModel
from app.core.base_service import BaseService
from app.services.document_loader import SimpleTextLoader
import os
import hashlib
import json
from datetime import datetime
import pytz
from app.utils.time_manager import get_current_timestamp

class ChromaService(BaseService, IVectorStore):
    """Service for handling vector store operations using ChromaDB"""
    _instance = None
    
    def __new__(cls, config: IConfiguration, embedding_model: IEmbeddingModel, document_loader: SimpleTextLoader):
        if cls._instance is None:
            cls._instance = super(ChromaService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: IConfiguration, embedding_model: IEmbeddingModel, document_loader: SimpleTextLoader):
        if not hasattr(self, 'initialized'):
            super().__init__(config, "chroma_service")
            self._embedding_model = embedding_model
            self._vector_store = None
            self._persist_directory = config.settings.CHROMA_PERSIST_DIRECTORY
            self._document_loader = document_loader
    
    def _initialize(self) -> None:
        """Initialize the vector store"""
        try:
            self.logger.info("Initializing ChromaDB")
            # Ensure persist directory exists
            os.makedirs(self._persist_directory, exist_ok=True)
            
            # Initialize ChromaDB with persistence
            self._vector_store = Chroma(
                persist_directory=self._persist_directory,
                embedding_function=self._embedding_model.model,
                collection_name="hr_policies"
            )
            
            # Load any existing data
            # self._vector_store.persist()
            self.logger.info("Successfully initialized ChromaDB")
        except Exception as e:
            self.logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def _shutdown(self) -> None:
        """Clean up resources"""
        self._vector_store = None
    
    def add_document(self, document: Document) -> str:
        """
        Add a document to ChromaDB
        
        Args:
            document (Document): Document to add
            
        Returns:
            str: ID of the added document
        """
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        try:
            # Add timestamps to metadata
            current_time = get_current_timestamp()
            document.metadata.update({
                "created_at": current_time,
                "updated_at": current_time
            })
            
            # Add document to ChromaDB
            ids = self._vector_store.add_documents([document])
            
            # Ensure changes are persisted
            # self._vector_store.persist()
            
            self.logger.info(f"Document added successfully: {document.metadata.get('source', 'Unknown')}")
            return ids[0] if ids else ""
            
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        for doc in documents:
            self.add_document(doc)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        return self._vector_store.similarity_search(query, k=k)
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents from the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        
        # Get all documents from ChromaDB
        results = self._vector_store.get()
        
        # If no documents found, return empty list
        if not results or not results.get('documents'):
            return []
            
        documents = []
            
        for i in range(len(results['ids'])):
            doc = {
                "id": results['ids'][i],
                "content": results['documents'][i],
                "metadata": results['metadatas'][i]
            }
            documents.append(doc)
        
        return documents
    
    def delete_document(self, document_id: str) -> None:
        """Delete a document from the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        try:
            self._vector_store._collection.delete(ids=[document_id])
            # self._vector_store.persist()
            
            self.logger.info(f"Successfully deleted document with ID: {document_id}")
        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def delete_all(self) -> None:
        """Delete all documents from the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
        try:
            # Get all document IDs
            results = self._vector_store.get()
            if results['ids']:
                # Delete all documents by their IDs
                self._vector_store._collection.delete(ids=results['ids'])
                # self._vector_store.persist()
            
            self.logger.info("Successfully deleted all data from ChromaDB")
        except Exception as e:
            self.logger.error(f"Error deleting ChromaDB data: {str(e)}")
            raise
    
    def update_document(self, document_id: str, new_content: str, new_metadata: Optional[Dict] = None) -> None:
        """Update an existing document in ChromaDB"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        try:
            # First delete the old document
            self.delete_document(document_id)
            
            # Then add the new document with updated timestamp
            if not new_metadata:
                new_metadata = {}
            
            new_metadata['updated_at'] = get_current_timestamp()
            
            new_doc = Document(
                page_content=new_content,
                metadata=new_metadata
            )
            self.add_document(new_doc)
            
            self.logger(f"Successfully updated document with ID: {document_id}")
        except Exception as e:
            self.logger.error(f"Error updating document: {str(e)}")
            raise
    
    def sync_directory(self, directory: str) -> Dict[str, int]:
        """Sync documents from a directory to the vector store"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
            
        if not os.path.exists(directory):
            self.logger.warning(f"Directory {directory} does not exist")
            return {
                "total_files": 0,
                "processed_files": 0,
                "skipped_files": 0,
                "error_files": 0
            }
        
        stats = {
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "error_files": 0
        }
            
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                stats["total_files"] += 1
                file_path = os.path.join(directory, filename)
                try:
                    if not self.is_file_processed(file_path):
                        self.logger.info(f"Processing new file: {filename}")
                        # Process the file using document loader
                        document = self._document_loader.load_file(file_path)
                        split_docs = self._document_loader.split_documents([document])
                        
                        # Add documents to ChromaDB
                        for doc in split_docs:
                            # Add source file information to metadata
                            doc.metadata.update({
                                "source": filename,
                                "file_modified_at": get_current_timestamp(),
                                "document_type": "hr_policy",
                                "content_type": "text/plain"
                            })
                            self.add_document(doc)
                            stats["processed_files"] += 1
                    else:
                        self.logger.info(f"File already processed: {filename}")
                        stats["skipped_files"] += 1
                except Exception as e:
                    self.logger.error(f"Error processing file {filename}: {str(e)}")
                    stats["error_files"] += 1
        
        return stats
    
    def is_file_processed(self, file_path: str) -> bool:
        """Check if a file has been processed"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        try:
            # Get the filename from the path
            filename = os.path.basename(file_path)
            
            # Check if any documents exist with this filename in metadata
            results = self._vector_store.get(
                where={"source": filename}
            )
            
            return len(results.get('documents', [])) > 0
        except Exception as e:
            self.logger.error(f"Error checking if file is processed: {str(e)}")
            return False
    
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
    
    def _should_update_document(self, file_path: str) -> bool:
        """Check if a document should be updated"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        try:
            # Get existing documents for this file
            existing_docs = self._vector_store.get(
                where={"source": file_path}
            )
            
            # If no existing documents, we should process it
            if not existing_docs or not existing_docs.get('documents'):
                return True
                
            # Get the hash of the current file
            current_hash = self._get_file_hash(os.path.join("data", "raw", file_path))
            
            # Get the hash from the first document's metadata
            stored_hash = existing_docs['metadatas'][0].get('hash')
            
            # If hashes don't match, we should update
            return current_hash != stored_hash
            
        except Exception as e:
            self.logger.error(f"Error checking if document should be updated: {str(e)}")
            return True  # If there's an error, we should process the file
    
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

    def get_document_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection"""
        if not self.is_initialized:
            raise RuntimeError("ChromaService not initialized")
            
        try:
            results = self._vector_store.get()
            info = {
                'total_documents': len(results['ids']),
                'total_chunks': len(results['ids']),
                'collection_name': self._vector_store._collection.name,
                'embedding_dimension': len(results['embeddings'][0]) if results['embeddings'] else 0,
                'persist_directory': self._persist_directory,
                'total_files': len(os.listdir(self._persist_directory))
            }
            
            self.logger.info(f"Retrieved ChromaDB info: {info}")
            return info
        except Exception as e:
            self.logger.error(f"Error retrieving ChromaDB info: {str(e)}")
            raise
