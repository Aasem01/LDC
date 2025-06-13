from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from app.services.chroma_service import chroma_service
from app.services.document_loader import document_loader
from app.utils.logger import api_logger
from langchain.schema import Document
import os
import pytz
from app.models.chroma_schemas import (
    DocumentRequest,
    DocumentUpdateRequest,
    DocumentListResponse,
    UploadResponse,
    ChromaInfoResponse,
    ProcessingStats
)
from app.utils.time_manager import measure_time

# Create router
chroma_router = APIRouter(tags=["chroma"], prefix="/chroma")

# ChromaDB CRUD Endpoints
@measure_time
@chroma_router.get("/documents", response_model=DocumentListResponse)
async def get_all_documents():
    """Get all documents from ChromaDB"""
    try:
        documents = chroma_service.get_all_documents()
        return DocumentListResponse(documents=documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@measure_time
@chroma_router.get("/info", response_model=ChromaInfoResponse)
async def get_chroma_info():
    """Get information about the ChromaDB collection"""
    try:
        return chroma_service.get_document_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@measure_time
@chroma_router.delete("/all")
async def delete_all_documents():
    """Delete all documents from ChromaDB"""
    try:
        chroma_service.delete_all()
        return {"message": "All documents deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@measure_time
@chroma_router.post("/sync", response_model=ProcessingStats)
async def sync_documents(force: bool = Query(False, description="Force re-embedding of all files")):
    """
    Synchronize all .txt files in the data/raw directory with ChromaDB.
    This will process all files and update ChromaDB accordingly.
    
    Args:
        force (bool): If True, deletes all existing documents and re-embeds all files
    """
    try:
        raw_dir = os.path.join("data", "raw")
        
        if force:
            # Delete all documents first
            chroma_service.delete_all()
            api_logger.info("Force sync: Deleted all existing documents")
        
        # Process the directory
        stats = chroma_service.sync_directory(raw_dir)
        
        # Create ProcessingStats object with the correct field names
        return ProcessingStats(
            total_files=stats["total_files"],
            processed_files=stats["processed_files"],
            skipped_files=stats["skipped_files"],
            error_files=stats["error_files"]
        )
    except Exception as e:
        api_logger.error(f"Error syncing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@measure_time
@chroma_router.post("/text")
async def add_text(request: DocumentRequest):
    """Add a new free text to ChromaDB"""
    try:
        document = Document(
            page_content=request.content,
            metadata=request.metadata or {}
        )
        chroma_service.add_document(document)
        return {"message": "Text added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@measure_time
@chroma_router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a text file and add its contents to ChromaDB.
    If the file has already been processed, it will be skipped.
    
    Args:
        file (UploadFile): The text file to upload
        
    Returns:
        UploadResponse: Status message and document count
    """
    try:
        # Validate file type
        if not file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=400,
                detail="Only .txt files are supported"
            )

        # Check if file has already been processed
        if chroma_service.is_file_processed(file.filename):
            existing_docs = chroma_service.get_file_documents(file.filename)
            return UploadResponse(
                message="File already processed and stored in ChromaDB",
                document_count=len(existing_docs),
                processed_count=0,
                skipped_count=len(existing_docs),
                filename=file.filename,
                status="skipped"
            )

        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Create document directly from content
        document = Document(
            page_content=content_str,
            metadata={
                "source": os.path.basename(file.filename),
                "file_modified_at": datetime.now(pytz.UTC).isoformat(),
                "document_type": "hr_policy",
                "content_type": "text/plain"
            }
        )
        
        # Split document into chunks using the singleton instance
        split_docs = document_loader.split_documents([document])
        
        # Track processing stats
        processed_count = 0
        skipped_count = 0
        
        # Add documents to ChromaDB
        for doc in split_docs:
            # Check if document needs updating based on filename
            if chroma_service._should_update_document(file.filename, doc.metadata):
                chroma_service.add_document(doc)
                processed_count += 1
            else:
                skipped_count += 1
        
        return UploadResponse(
            message="File processed successfully",
            document_count=len(split_docs),
            processed_count=processed_count,
            skipped_count=skipped_count,
            filename=file.filename,
            status="processed"
        )
            
    except Exception as e:
        api_logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@measure_time
@chroma_router.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document from ChromaDB"""
    try:
        chroma_service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@measure_time
@chroma_router.put("/document/{document_id}")
async def update_document(document_id: str, request: DocumentUpdateRequest):
    """Update an existing document in ChromaDB"""
    try:
        chroma_service.update_document(
            document_id,
            request.content,
            request.metadata
        )
        return {"message": f"Document {document_id} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 