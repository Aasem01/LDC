from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.core.application import Application
from app.utils.logger import api_logger
from app.models.rag_schemas import QueryRequest, QueryResponse
from app.utils.time_manager import measure_time, get_current_timestamp
from app.api.interactions import create_interaction
from app.schemas.interaction_schema import InteractionCreate, DocumentMetadata
from app.core.database import get_db
from sqlalchemy.orm import Session

# Create router
rag_router = APIRouter(tags=["rag"], prefix="/rag")

def get_application() -> Application:
    """Dependency to get the application instance"""
    return Application.get_instance()

@measure_time
@rag_router.post("/rag_chat", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    app: Application = Depends(get_application),
    db: Session = Depends(get_db)
):
    """
    Query the RAG system with a question.
    
    Args:
        request (QueryRequest): The question to ask
        
    Returns:
        QueryResponse: The answer and source documents
    """
    api_logger.info(f"Received request from user {request.user_id}\nquestion: {request.question}")
    try:
        result = await app.rag_service.get_answer(request.question)
        api_logger.info("Successfully processed query")
        api_logger.debug(f"Found {len(result['source_documents'])} relevant documents")
        
        # Format source documents according to schema
        formatted_documents = []
        for doc in result['source_documents']:
            metadata = doc.get('metadata', {})
            formatted_doc = DocumentMetadata(
                document_type=metadata.get('document_type', 'text/plain'),
                source=metadata.get('source', 'unknown')
            )
            formatted_documents.append(formatted_doc)
        
        # Create an InteractionCreate object
        interaction = InteractionCreate(
            user_id=str(request.user_id),
            query=request.question,
            answer=result["answer"],
            timestamp=get_current_timestamp(),
            source_documents=formatted_documents
        )
        
        # Add database write to background tasks
        background_tasks.add_task(create_interaction, interaction, db)
        
        return QueryResponse(**result)
    except Exception as e:
        api_logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))