from typing import List, Dict, Optional
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from app.core.config import get_settings
from app.services.document_loader import document_loader
from app.utils.logger import chroma_logger
import os
import shutil
from datetime import datetime
import pytz

settings = get_settings()

class ChromaService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self.embeddings = None  # Will be set by EmbeddingService
        self.vector_store = None

    def initialize(self, embeddings):
        """Initialize the ChromaDB service with embeddings"""
        self.embeddings = embeddings
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            chroma_logger.info("ChromaDB service initialized successfully")
        except Exception as e:
            chroma_logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(pytz.UTC).isoformat()

    def _should_update_document(self, file_path: str, existing_metadata: Optional[Dict] = None) -> bool:
        """Check if document should be updated based on file timestamp"""
        if not existing_metadata or 'updated_at' not in existing_metadata:
            return True
        
        current_time = datetime.now(pytz.UTC)
        stored_datetime = datetime.fromisoformat(existing_metadata['updated_at'])
        
        return current_time > stored_datetime

    def is_file_processed(self, filename: str) -> bool:
        """
        Check if a file has already been processed and stored in ChromaDB.
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if file exists in ChromaDB, False otherwise
        """
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            # Get all documents
            results = self.vector_store.get()
            
            # Check if any document has this filename as source
            for metadata in results['metadatas']:
                if metadata.get('source') == filename:
                    return True
                    
            return False
        except Exception as e:
            chroma_logger.error(f"Error checking file existence: {str(e)}")
            raise

    def get_file_documents(self, filename: str) -> List[Dict]:
        """
        Get all documents associated with a specific file.
        
        Args:
            filename (str): Name of the file to get documents for
            
        Returns:
            List[Dict]: List of documents associated with the file
        """
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            # Get all documents
            results = self.vector_store.get()
            documents = []
            
            # Filter documents by source filename
            for i in range(len(results['ids'])):
                if results['metadatas'][i].get('source') == filename:
                    doc = {
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    documents.append(doc)
            
            return documents
        except Exception as e:
            chroma_logger.error(f"Error getting file documents: {str(e)}")
            raise

    def get_all_documents(self) -> List[Dict]:
        """
        Get all documents from ChromaDB
        
        Returns:
            List[Dict]: List of documents with their metadata
        """
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            results = self.vector_store.get()
            documents = []
            
            for i in range(len(results['ids'])):
                doc = {
                    "id": results['ids'][i],
                    "content": results['documents'][i],
                    "metadata": results['metadatas'][i]
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            chroma_logger.error(f"Error getting all documents: {str(e)}")
            raise

    def get_document_info(self) -> Dict:
        """Get information about the ChromaDB collection"""
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            results = self.vector_store.get()
            info = {
                'total_documents': len(results['ids']),
                'collection_name': self.vector_store._collection.name,
                'embedding_dimension': len(results['embeddings'][0]) if results['embeddings'] else 0,
                'persist_directory': self.persist_directory
            }
            
            chroma_logger.info(f"Retrieved ChromaDB info: {info}")
            return info
        except Exception as e:
            chroma_logger.error(f"Error retrieving ChromaDB info: {str(e)}")
            raise

    def delete_all(self):
        """Delete all data from ChromaDB"""
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            # Get all document IDs
            results = self.vector_store.get()
            if results['ids']:
                # Delete all documents by their IDs
                self.vector_store._collection.delete(ids=results['ids'])
                self.vector_store.persist()
            
            chroma_logger.info("Successfully deleted all data from ChromaDB")
        except Exception as e:
            chroma_logger.error(f"Error deleting ChromaDB data: {str(e)}")
            raise

    def add_document(self, document: Document) -> str:
        """
        Add a document to ChromaDB
        
        Args:
            document (Document): Document to add
            
        Returns:
            str: ID of the added document
        """
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            # Add timestamps to metadata
            current_time = datetime.now(pytz.UTC).isoformat()
            document.metadata.update({
                "created_at": current_time,
                "updated_at": current_time
            })
            
            # Add document to ChromaDB
            self.vector_store.add_documents([document])
            self.vector_store.persist()
            
            chroma_logger.info(f"Document added successfully: {document.metadata.get('source', 'Unknown')}")
            return document.metadata.get("id", "")
            
        except Exception as e:
            chroma_logger.error(f"Error adding document: {str(e)}")
            raise

    def delete_document(self, document_id: str):
        """Delete a specific document from ChromaDB"""
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            self.vector_store._collection.delete(ids=[document_id])
            self.vector_store.persist()
            
            chroma_logger.info(f"Successfully deleted document with ID: {document_id}")
        except Exception as e:
            chroma_logger.error(f"Error deleting document: {str(e)}")
            raise

    def update_document(self, document_id: str, new_content: str, new_metadata: Optional[Dict] = None):
        """Update an existing document in ChromaDB"""
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            # First delete the old document
            self.delete_document(document_id)
            
            # Then add the new document with updated timestamp
            if not new_metadata:
                new_metadata = {}
            
            new_metadata['updated_at'] = self._get_current_timestamp()
            
            new_doc = Document(
                page_content=new_content,
                metadata=new_metadata
            )
            self.add_document(new_doc)
            
            chroma_logger.info(f"Successfully updated document with ID: {document_id}")
        except Exception as e:
            chroma_logger.error(f"Error updating document: {str(e)}")
            raise

    def sync_directory(self, directory_path: str) -> Dict:
        """
        Synchronize all files in the directory with ChromaDB.
        This will process all .txt files in the directory and update ChromaDB accordingly.
        
        Args:
            directory_path (str): Path to the directory containing txt files
            
        Returns:
            Dict: Processing statistics
        """
        try:
            if not self.vector_store:
                raise ValueError("ChromaDB not initialized")
            
            # Ensure directory exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
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
            
            # Process all txt files
            for filename in os.listdir(directory_path):
                if not filename.endswith('.txt'):
                    continue
                    
                stats["total_files"] += 1
                file_path = os.path.join(directory_path, filename)
                
                try:
                    # Check if file has already been processed
                    if self.is_file_processed(filename):
                        existing_docs = self.get_file_documents(filename)
                        stats["skipped_files"] += len(existing_docs)
                        continue
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create document
                    document = Document(
                        page_content=content,
                        metadata={
                            "source": filename,
                            "file_modified_at": datetime.now(pytz.UTC).isoformat(),
                            "document_type": "hr_policy",
                            "content_type": "text/plain"
                        }
                    )
                    
                    # Split document into chunks using the singleton instance
                    split_docs = document_loader.split_documents([document])
                    
                    # Add documents to ChromaDB
                    for doc in split_docs:
                        # Check if document needs updating based on filename
                        if self._should_update_document(filename, doc.metadata):
                            self.add_document(doc)
                            stats["processed_files"] += 1
                        else:
                            stats["skipped_files"] += 1
                    
                    chroma_logger.info(f"Successfully processed file: {filename}")
                    
                except Exception as e:
                    chroma_logger.error(f"Error processing file {filename}: {str(e)}")
                    stats["error_files"] += 1
                    continue
            
            chroma_logger.info(f"Directory sync complete. Stats: {stats}")
            return stats
            
        except Exception as e:
            chroma_logger.error(f"Error syncing directory: {str(e)}")
            raise

chroma_service = ChromaService()
