from app.core.middleware import validate_api_key
from app.utils.logger import api_logger
from app.utils.time_manager import measure_time
from fastapi import Request
from main import app
from fastapi.middleware.cors import CORSMiddleware

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7000", "http://127.0.0.1:7000", "localhost:7000", "127.0.0.1:7000"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type", "Accept"],
    expose_headers=["*"],
    max_age=3600,
)

@measure_time
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """
    Middleware to validate API key and origin for all requests
    """
    api_logger.info(f"Processing request: {request.method} {request.url.path}")
    api_logger.info(f"Request headers: {dict(request.headers)}")
    
    # Validate API key and origin
    validation_response = await validate_api_key(request)
    if validation_response is not None:
        return validation_response

    # If validation passes, proceed with the request
    response = await call_next(request)
    return response

