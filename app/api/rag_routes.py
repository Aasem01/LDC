from fastapi import APIRouter, HTTPException
from app.services.rag_service import rag_service
from app.utils.logger import api_logger
from app.models.rag_schemas import QueryRequest, QueryResponse
from app.utils.time_manager import measure_time

# Create router
rag_router = APIRouter(tags=["rag"], prefix="/rag")

@measure_time
@rag_router.post("/rag_chat", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system with a question.
    
    Args:
        request (QueryRequest): The question to ask
        
    Returns:
        QueryResponse: The answer and source documents
    """
    api_logger.info(f"Received request from user {request.user_id}\nquestion: {request.question}")
    try:
        result = await rag_service.get_answer(request.question)
        api_logger.info("Successfully processed query")
        api_logger.debug(f"Found {len(result['source_documents'])} relevant documents")
        return QueryResponse(**result)
    except Exception as e:
        api_logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 