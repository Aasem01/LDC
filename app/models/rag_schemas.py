from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    """Schema for RAG query request"""
    question: str

class QueryResponse(BaseModel):
    """Schema for RAG query response"""
    answer: str
    source_documents: List[Dict] 