from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.interaction_service import InteractionService
from app.schemas.interaction_schema import InteractionCreate, InteractionResponse, InteractionList
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/interactions/", response_model=InteractionResponse)
def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new interaction with associated document metadata
    """
    service = InteractionService(db)
    response = service.create_interaction(interaction)
    logger.info(f"Created interaction response: {response}")
    return response

@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific interaction by ID
    """
    service = InteractionService(db)
    interaction = service.get_interaction(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    logger.info(f"Retrieved interaction: {interaction}")
    return interaction

@router.get("/interactions/user/{user_id}", response_model=InteractionList)
def get_user_interactions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all interactions for a specific user
    """
    service = InteractionService(db)
    interactions = service.get_user_interactions(user_id)
    response = InteractionList(interactions=interactions, total=len(interactions))
    logger.info(f"Retrieved user interactions: {response}")
    return response

@router.get("/interactions/", response_model=InteractionList)
def get_all_interactions(
    db: Session = Depends(get_db)
):
    """
    Get all interactions
    """
    service = InteractionService(db)
    interactions = service.get_all_interactions()
    response = InteractionList(interactions=interactions, total=len(interactions))
    logger.info(f"Retrieved all interactions: {response}")
    return response

@router.delete("/interactions/user/{user_id}")
def delete_user_data(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete all interactions and their associated data for a specific user
    """
    service = InteractionService(db)
    deleted_count = service.delete_user_data(user_id)
    response = {"message": f"Successfully deleted {deleted_count} interactions for user {user_id}"}
    logger.info(f"Delete user data response: {response}")
    return response