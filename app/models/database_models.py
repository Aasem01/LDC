from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class InteractionLog(Base):
    __tablename__ = 'interaction_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    query = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    created_at = Column(String, nullable=False, server_default=func.now())
    updated_at = Column(String, nullable=False, server_default=func.now())
    
    # Relationships
    document_types = relationship("DocumentType", back_populates="interaction", cascade="all, delete-orphan")
    source_documents = relationship("SourceDocument", back_populates="interaction", cascade="all, delete-orphan")

class DocumentType(Base):
    __tablename__ = 'document_types'
    
    id = Column(Integer, primary_key=True)
    interaction_id = Column(Integer, ForeignKey('interaction_logs.id', ondelete='CASCADE'), nullable=False)
    document_type = Column(String, nullable=False)
    created_at = Column(String, nullable=False, server_default=func.now())
    
    # Relationship
    interaction = relationship("InteractionLog", back_populates="document_types")

class SourceDocument(Base):
    __tablename__ = 'source_documents'
    
    id = Column(Integer, primary_key=True)
    interaction_id = Column(Integer, ForeignKey('interaction_logs.id', ondelete='CASCADE'), nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(String, nullable=False, server_default=func.now())
    
    # Relationship
    interaction = relationship("InteractionLog", back_populates="source_documents") 