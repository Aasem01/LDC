# app/services/document_loader.py

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional
from app.core.config import get_settings
from app.utils.logger import document_logger
import os
from datetime import datetime
import pytz

settings = get_settings()


class SimpleTextLoader:
    """
    A minimal text loader to avoid Unix-only modules (like pwd).
    Compatible with LangChain Document schema.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimpleTextLoader, cls).__new__(cls)
            cls._instance.chunk_size = 500
            cls._instance.chunk_overlap = 100
        return cls._instance

    def __init__(self):
        # Initialize only if not already initialized
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.path = ""

    def set_path(self, path: str):
        """Set the current file path"""
        self.path = path

    def load(self) -> List[Document]:
        """
        Load documents from a file.

        Returns:
            List[Document]: List of loaded documents
        """
        document_logger.info(f"Loading document from: {self.path}")
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Get file timestamp
            file_timestamp = os.path.getmtime(self.path)
            file_datetime = datetime.fromtimestamp(file_timestamp, pytz.UTC)
            
            documents = [Document(
                page_content=text,
                metadata={
                    "source": self.path,
                    "file_modified_at": file_datetime.isoformat()
                }
            )]
            document_logger.info(f"Successfully loaded {len(documents)} documents")
            return documents
        except Exception as e:
            document_logger.error(f"Failed to read file: {self.path} - {str(e)}")
            raise

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents (List[Document]): List of documents to split

        Returns:
            List[Document]: List of split documents
        """
        document_logger.info(f"Splitting {len(documents)} documents into chunks")
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ".", " "],
                is_separator_regex=False
            )
            split_docs = text_splitter.split_documents(documents)
            document_logger.info(f"Successfully split into {len(split_docs)} chunks")
            return split_docs
        except Exception as e:
            document_logger.error(f"Error splitting documents: {str(e)}")
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
        document_logger.info(f"Processing directory: {directory_path}")
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
                document_logger.info(f"Created directory: {directory_path}")
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
                        document_logger.info(f"Skipping already processed file: {filename}")
                        stats["skipped_files"] += 1
                        continue
                    
                    # Load and process the document
                    self.set_path(file_path)
                    documents = self.load()
                    split_docs = self.split_documents(documents)
                    
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
                    document_logger.error(f"Error processing file {filename}: {str(e)}")
                    stats["errors"] += 1
                    continue
                    
            document_logger.info(f"Directory processing complete. Stats: {stats}")
            return stats
            
        except Exception as e:
            document_logger.error(f"Error processing directory: {str(e)}")
            raise


# Create singleton instance
document_loader = SimpleTextLoader()
