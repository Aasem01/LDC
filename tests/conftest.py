import os
os.environ["API_KEY"] = "test-api-key"
os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"
os.environ["ALLOWED_ORIGINS"] = '["http://localhost:7000", "http://127.0.0.1:7000", "testclient"]'

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.models.database_models import InteractionLog, DocumentType, SourceDocument

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_interaction(db_session):
    # Create a sample interaction
    interaction = InteractionLog(
        user_id="test-user-123",
        query="test query",
        answer="test answer",
        timestamp="2024-01-01T00:00:00Z"
    )
    
    # Add document types
    interaction.document_types.append(
        DocumentType(document_type="test_doc_type")
    )
    
    # Add sources
    interaction.source_documents.append(
        SourceDocument(source="test_source.txt")
    )
    
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)
    return interaction 