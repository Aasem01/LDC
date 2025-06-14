import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database_models import InteractionLog, DocumentType, SourceDocument
from app.schemas.interaction_schema import InteractionCreate, DocumentMetadata

client = TestClient(app)

def test_create_interaction(db_session):
    # Test data
    interaction_data = {
        "user_id": "test-user-123",
        "query": "test query",
        "answer": "test answer",
        "timestamp": "2024-01-01T00:00:00Z",
        "source_documents": [
            {
                "document_type": "test_doc_type",
                "source": "test_source.txt"
            }
        ]
    }
    
    # Make request
    response = client.post("/api/v1/interactions/", json=interaction_data)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == interaction_data["user_id"]
    assert data["query"] == interaction_data["query"]
    assert data["answer"] == interaction_data["answer"]
    assert data["document_types"] == ["test_doc_type"]
    assert data["sources"] == ["test_source.txt"]

def test_get_interaction(db_session, sample_interaction):
    # Make request
    response = client.get(f"/api/v1/interactions/{sample_interaction.id}")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_interaction.id
    assert data["user_id"] == sample_interaction.user_id
    assert data["query"] == sample_interaction.query
    assert data["answer"] == sample_interaction.answer

def test_get_user_interactions(db_session, sample_interaction):
    # Make request
    response = client.get(f"/api/v1/interactions/user/{sample_interaction.user_id}")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["interactions"]) == 1
    assert data["interactions"][0]["user_id"] == sample_interaction.user_id

def test_get_all_interactions(db_session, sample_interaction):
    # Make request
    response = client.get("/api/v1/interactions/")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["interactions"]) == 1
    assert data["interactions"][0]["id"] == sample_interaction.id

def test_delete_user_data(db_session, sample_interaction):
    # Make request
    response = client.delete(f"/api/v1/interactions/user/{sample_interaction.user_id}")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Successfully deleted 1 interactions for user {sample_interaction.user_id}"
    
    # Verify deletion
    response = client.get(f"/api/v1/interactions/user/{sample_interaction.user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["interactions"]) == 0

def test_get_nonexistent_interaction(db_session):
    # Make request
    response = client.get("/api/v1/interactions/999")
    
    # Assertions
    assert response.status_code == 404
    assert response.json()["detail"] == "Interaction not found"

def test_delete_nonexistent_user(db_session):
    # Make request
    response = client.delete("/api/v1/interactions/user/nonexistent-user")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully deleted 0 interactions for user nonexistent-user" 