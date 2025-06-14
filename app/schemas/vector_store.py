from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Document(BaseModel):
    """Schema for a document in the vector store"""
    id: str = Field(..., description="Unique identifier of the document")
    content: str = Field(..., description="The content of the document")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata for the document")

class VectorStoreResponse(BaseModel):
    """Schema for vector store response"""
    documents: List[Document] = Field(..., description="List of documents in the vector store") 