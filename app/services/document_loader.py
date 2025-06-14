# app/services/document_loader.py

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional
from app.core.config import settings
from app.utils.logger import document_logger
from app.core.base_service import BaseService
from app.core.interfaces import IConfiguration
import os
from datetime import datetime
import pytz

class SimpleTextLoader(BaseService):
    """
    A service for loading and processing text documents.
    Handles file loading, text splitting, and document processing.
    """
    _instance = None

    def __new__(cls, config: IConfiguration):
        if cls._instance is None:
            cls._instance = super(SimpleTextLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: IConfiguration):
        if not hasattr(self, 'initialized'):
            super().__init__(config, "document_loader")
            self.chunk_size = config.settings.CHUNK_SIZE
            self.chunk_overlap = config.settings.CHUNK_OVERLAP
            self._text_splitter = None

    def _initialize(self) -> None:
        """Initialize the text splitter"""
        try:
            self.logger.info("Initializing text splitter")
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ".", " "],
                is_separator_regex=False
            )
            self.logger.info("Successfully initialized text splitter")
        except Exception as e:
            self.logger.error(f"Error initializing text splitter: {str(e)}")
            raise

    def _shutdown(self) -> None:
        """Clean up resources"""
        self._text_splitter = None

    def load_file(self, file_path: str) -> Document:
        """
        Load a single file and return it as a Document.

        Args:
            file_path (str): Path to the file to load

        Returns:
            Document: Loaded document with metadata
        """
        if not self.is_initialized:
            raise RuntimeError("DocumentLoader not initialized")

        self.logger.info(f"Loading file: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Get file timestamp
            file_timestamp = os.path.getmtime(file_path)
            file_datetime = datetime.fromtimestamp(file_timestamp, pytz.UTC)
            
            document = Document(
                page_content=text,
                metadata={
                    "source": os.path.basename(file_path),
                    "file_modified_at": file_datetime.isoformat(),
                    "document_type": "hr_policy",
                    "content_type": "text/plain"
                }
            )
            
            self.logger.info(f"Successfully loaded file: {file_path}")
            return document
        except Exception as e:
            self.logger.error(f"Failed to load file: {file_path} - {str(e)}")
            raise

    def process_file(self, file_path: str) -> List[Document]:
        """
        Process a single file: load it and split into chunks.

        Args:
            file_path (str): Path to the file to process

        Returns:
            List[Document]: List of processed document chunks
        """
        if not self.is_initialized:
            raise RuntimeError("DocumentLoader not initialized")

        try:
            # Load the document
            document = self.load_file(file_path)
            
            # Split into chunks
            split_docs = self.split_documents([document])
            
            self.logger.info(f"Successfully processed file: {file_path}")
            return split_docs
        except Exception as e:
            self.logger.error(f"Error processing file: {file_path} - {str(e)}")
            raise

    def process_directory(self, directory_path: str, chroma_service) -> Dict:
        """
        Process all txt files in a directory and add them to ChromaDB.
        Files that have already been processed will be skipped.
        
        Args:
            directory_path (str): Path to the directory containing txt files
            chroma_service: ChromaService instance
            
        Returns:
            Dict: Processing statistics
        """
        if not self.is_initialized:
            raise RuntimeError("DocumentLoader not initialized")

        self.logger.info(f"Processing directory: {directory_path}")
        stats = {
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "errors": 0
        }
        
        try:
            # Ensure directory exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                self.logger.info(f"Created directory: {directory_path}")
                return stats
                
            # Process all txt files
            for filename in os.listdir(directory_path):
                if not filename.endswith('.txt'):
                    continue
                    
                stats["total_files"] += 1
                file_path = os.path.join(directory_path, filename)
                
                try:
                    # Check if file has already been processed
                    if chroma_service.is_file_processed(filename):
                        self.logger.info(f"Skipping already processed file: {filename}")
                        stats["skipped_files"] += 1
                        continue
                    
                    # Load and process the document
                    document = self.load_file(file_path)
                    split_docs = self.split_documents([document])
                    
                    # Add documents to ChromaDB
                    for doc in split_docs:
                        # Add source file information to metadata
                        doc.metadata.update({
                            "source": filename,
                            "file_modified_at": datetime.now(pytz.UTC).isoformat(),
                            "document_type": "hr_policy",
                            "content_type": "text/plain"
                        })
                        chroma_service.add_document(doc)
                        stats["processed_files"] += 1
                            
                except Exception as e:
                    self.logger.error(f"Error processing file {filename}: {str(e)}")
                    stats["errors"] += 1
                    continue
                    
            self.logger.info(f"Directory processing complete. Stats: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error processing directory: {str(e)}")
            raise

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents (List[Document]): List of documents to split

        Returns:
            List[Document]: List of split documents
        """
        if not self.is_initialized:
            raise RuntimeError("DocumentLoader not initialized")

        self.logger.info(f"Splitting {len(documents)} documents into chunks")
        try:
            split_docs = self._text_splitter.split_documents(documents)
            self.logger.info(f"Successfully split into {len(split_docs)} chunks")
            return split_docs
        except Exception as e:
            self.logger.error(f"Error splitting documents: {str(e)}")
            raise
