from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from langchain.schema import Document as LangchainDocument
import uuid

class DocumentCreate(BaseModel):
    """Schema for creating a new document"""
    content: str = Field(..., description="The content of the document")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for the document")
    
    def to_document(self) -> LangchainDocument:
        """Convert to Langchain Document"""
        if "id" not in self.metadata:
            self.metadata["id"] = str(uuid.uuid4())
        return LangchainDocument(
            page_content=self.content,
            metadata=self.metadata
        )

class DocumentResponse(BaseModel):
    """Schema for document operation response"""
    message: str = Field(..., description="Operation status message")
    document_id: str = Field(..., description="ID of the document") 