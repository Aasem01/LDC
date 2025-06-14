from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.interaction_schema import InteractionCreate, InteractionResponse
from app.models.database_models import InteractionLog

class InteractionService:
    def __init__(self, db: Session):
        self.repository = InteractionRepository(db)

    def create_interaction(self, interaction: InteractionCreate) -> InteractionResponse:
        # Extract unique document types and sources
        document_types = list(set(doc.document_type for doc in interaction.source_documents))
        sources = list(set(doc.source for doc in interaction.source_documents))

        # Create interaction with metadata
        db_interaction = self.repository.create_with_metadata(
            user_id=interaction.user_id,
            query=interaction.query,
            answer=interaction.answer,
            timestamp=interaction.timestamp,
            document_types=document_types,
            sources=sources
        )

        return self._to_response(db_interaction)

    def get_interaction(self, interaction_id: int) -> Optional[InteractionResponse]:
        interaction = self.repository.get_by_id(interaction_id)
        if interaction:
            return self._to_response(interaction)
        return None

    def get_user_interactions(self, user_id: str) -> List[InteractionResponse]:
        interactions = self.repository.get_by_user_id(user_id)
        return [self._to_response(interaction) for interaction in interactions]

    def get_all_interactions(self) -> List[InteractionResponse]:
        interactions = self.repository.get_all()
        return [self._to_response(interaction) for interaction in interactions]

    def delete_user_data(self, user_id: str) -> int:
        """
        Delete all interactions and their associated data for a specific user
        Returns the number of deleted interactions
        """
        return self.repository.delete_by_user_id(user_id)

    def _to_response(self, interaction: InteractionLog) -> InteractionResponse:
        return InteractionResponse(
            id=interaction.id,
            user_id=interaction.user_id,
            query=interaction.query,
            answer=interaction.answer,
            timestamp=interaction.timestamp,
            document_types=[dt.document_type for dt in interaction.document_types],
            sources=[sd.source for sd in interaction.source_documents],
            created_at=interaction.created_at,
            updated_at=interaction.updated_at
        ) 