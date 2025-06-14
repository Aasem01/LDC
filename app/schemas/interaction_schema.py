from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    document_type: str
    source: str

class InteractionCreate(BaseModel):
    user_id: str = Field(..., description="User's unique identifier")
    query: str = Field(..., description="User's question")
    answer: str = Field(..., description="Generated answer")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    source_documents: List[DocumentMetadata] = Field(..., description="List of source documents")

class InteractionResponse(BaseModel):
    id: int
    user_id: str
    query: str
    answer: str
    timestamp: str
    document_types: List[str]
    sources: List[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class InteractionList(BaseModel):
    interactions: List[InteractionResponse]
    total: int 