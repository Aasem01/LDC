from pydantic import BaseModel, Field
from typing import List, Dict, Any

class RAGRequest(BaseModel):
    """Schema for RAG question request"""
    question: str = Field(..., description="The question to ask")

class SourceDocument(BaseModel):
    """Schema for source document in RAG response"""
    content: str = Field(..., description="The content of the source document")
    metadata: Dict[str, Any] = Field(..., description="Metadata of the source document")

class RAGResponse(BaseModel):
    """Schema for RAG response"""
    answer: str = Field(..., description="The generated answer")
    source_documents: List[SourceDocument] = Field(..., description="Source documents used to generate the answer") 