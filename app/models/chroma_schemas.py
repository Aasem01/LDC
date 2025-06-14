from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DocumentRequest(BaseModel):
    """Schema for adding a new text document"""
    content: str
    metadata: Optional[Dict] = None

class DocumentUpdateRequest(BaseModel):
    """Schema for updating an existing document"""
    content: str
    metadata: Optional[Dict] = None

class DocumentResponse(BaseModel):
    """Response model for a single document"""
    id: str
    content: str
    metadata: Dict[str, Any]

class DocumentListResponse(BaseModel):
    """Response model for a list of documents"""
    documents: List[DocumentResponse]

class ProcessingStats(BaseModel):
    """Schema for document processing statistics"""
    total_files: int
    processed_files: int
    skipped_files: int
    error_files: int

class UploadResponse(BaseModel):
    """Schema for file upload response"""
    message: str
    document_count: int
    processed_count: int
    skipped_count: int
    filename: str
    status: str

class ChromaInfoResponse(BaseModel):
    """Schema for ChromaDB information response"""
    total_documents: int
    collection_name: str
    embedding_dimension: int 
    persist_directory: str
    total_chunks: int
    total_files: int