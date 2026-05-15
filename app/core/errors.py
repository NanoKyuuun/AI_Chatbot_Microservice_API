from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import logger
import time
import uuid

class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    
    if isinstance(exc, AppError):
        status_code = exc.status_code
        error_data = {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            },
            "meta": {
                "request_id": request_id,
                "timestamp": time.time()
            }
        }
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        error_data = {
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {}
            },
            "meta": {
                "request_id": request_id,
                "timestamp": time.time()
            }
        }
    elif isinstance(exc, RequestValidationError):
        status_code = 422
        error_data = {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()}
            },
            "meta": {
                "request_id": request_id,
                "timestamp": time.time()
            }
        }
    else:
        # Unexpected error
        logger.exception("unexpected_error", error=str(exc), path=request.url.path)
        status_code = 500
        error_data = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            },
            "meta": {
                "request_id": request_id,
                "timestamp": time.time()
            }
        }
    
    logger.error("request_failed", status_code=status_code, error_code=error_data["error"]["code"], path=request.url.path)
    return JSONResponse(status_code=status_code, content=error_data)
