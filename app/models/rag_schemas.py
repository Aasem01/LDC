from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
from uuid import UUID
class QueryRequest(BaseModel):
    """Schema for RAG query request"""
    question: str
    user_id: UUID

    @validator('user_id')
    def validate_user_id(cls, v):
        if not isinstance(v, UUID):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError('user_id must be a valid UUID4')
        return v

class QueryResponse(BaseModel):
    """Schema for RAG query response"""
    answer: str
    source_documents: List[Dict] 