from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.database_models import InteractionLog, DocumentType, SourceDocument

class InteractionRepository(BaseRepository[InteractionLog]):
    def __init__(self, session: Session):
        super().__init__(session)
        self.model = InteractionLog

    def create(self, entity: InteractionLog) -> InteractionLog:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, id: int) -> Optional[InteractionLog]:
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[InteractionLog]:
        return self.session.query(self.model).all()

    def get_by_user_id(self, user_id: str) -> List[InteractionLog]:
        return self.session.query(self.model).filter(self.model.user_id == user_id).all()

    def update(self, entity: InteractionLog) -> InteractionLog:
        self.session.merge(entity)
        self.session.commit()
        return entity

    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False

    def delete_by_user_id(self, user_id: str) -> int:
        """
        Delete all interactions and their associated data for a specific user
        Returns the number of deleted interactions
        """
        interactions = self.get_by_user_id(user_id)
        count = len(interactions)
        for interaction in interactions:
            self.session.delete(interaction)
        self.session.commit()
        return count

    def create_with_metadata(self, 
                           user_id: str, 
                           query: str, 
                           answer: str, 
                           timestamp: str,
                           document_types: List[str],
                           sources: List[str]) -> InteractionLog:
        """
        Create a new interaction log with associated document types and sources
        """
        interaction = InteractionLog(
            user_id=user_id,
            query=query,
            answer=answer,
            timestamp=timestamp
        )

        # Add document types
        for doc_type in document_types:
            interaction.document_types.append(
                DocumentType(document_type=doc_type)
            )

        # Add sources
        for source in sources:
            interaction.source_documents.append(
                SourceDocument(source=source)
            )

        return self.create(interaction) 