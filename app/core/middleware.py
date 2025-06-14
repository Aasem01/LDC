from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.utils.logger import api_logger
from typing import Dict, Any, Optional
from app.utils.time_manager import measure_time

api_key_header = APIKeyHeader(name="X-API-Key")

# Paths that don't require API key validation
EXCLUDED_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
    "/"
}

def create_error_response(status_code: int, detail: str, error_type: str) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "status": "error",
        "error": {
            "type": error_type,
            "message": detail,
            "code": status_code
        }
    }
@measure_time
async def validate_api_key(request: Request) -> Optional[JSONResponse]:
    """
    Middleware to validate API key and request origin.
    Returns None if validation passes, or a JSONResponse if validation fails.
    """
    # Skip validation for excluded paths
    if request.url.path in EXCLUDED_PATHS:
        api_logger.info(f"Skipping validation for excluded path: {request.url.path}")
        return None

    try:
        # Get all headers for debugging
        headers = dict(request.headers)
        api_logger.info(f"Request headers: {headers}")

        # Validate origin
        origin = request.headers.get("origin")
        api_logger.info(f"Origin header: {origin}")

        if not origin:
            # If no origin header, check referer
            referer = request.headers.get("referer")
            api_logger.info(f"Referer header: {referer}")
            
            if referer:
                origin = referer.split("//")[1].split("/")[0]
                api_logger.info(f"Extracted origin from referer: {origin}")
            else:
                origin = request.client.host
                api_logger.info(f"Using client host as origin: {origin}")

        api_logger.info(f"Final request origin: {origin}")

        # Check if origin is allowed
        allowed_origins = settings.ALLOWED_ORIGINS
        api_logger.info(f"Checking against allowed origins: {allowed_origins}")
        
        if not any(allowed_origin in origin for allowed_origin in allowed_origins):
            error_detail = (
                f"Access denied. The request origin '{origin}' is not allowed. "
                f"This API can only be accessed through the authorized .NET backend at {settings.ALLOWED_ORIGINS[0]}"
            )
            api_logger.warning(f"Validation failed: {error_detail}")
            return JSONResponse(
                status_code=403,
                content=create_error_response(
                    status_code=403,
                    detail=error_detail,
                    error_type="ValidationError"
                )
            )

        # Validate API key
        api_key = request.headers.get("X-API-Key")
        api_logger.info(f"API Key present: {bool(api_key)}")
        
        if not api_key:
            error_detail = "Authentication required. Please provide a valid API key in the X-API-Key header."
            api_logger.warning(f"Validation failed: {error_detail}")
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    status_code=401,
                    detail=error_detail,
                    error_type="AuthenticationError"
                )
            )
        
        if api_key != settings.API_KEY:
            error_detail = "Invalid API key. Please check your credentials and try again."
            api_logger.warning(f"Validation failed: {error_detail}")
            return JSONResponse(
                status_code=401,
                content=create_error_response(
                    status_code=401,
                    detail=error_detail,
                    error_type="AuthenticationError"
                )
            )
            
        api_logger.info("API key validation successful")
        return None

    except Exception as e:
        api_logger.error(f"Error during validation: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                status_code=500,
                detail="An unexpected error occurred while processing your request.",
                error_type="InternalServerError"
            )
        ) 