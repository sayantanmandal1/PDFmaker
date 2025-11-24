"""
Global exception handlers and custom exceptions for the FastAPI application.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from openai import RateLimitError, APIError, APIConnectionError
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIException(HTTPException):
    """Base API exception with consistent error format."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        field_errors: Optional[Dict[str, List[str]]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.field_errors = field_errors


class ValidationException(APIException):
    """Exception for validation errors with field-specific messages."""
    
    def __init__(self, field_errors: Dict[str, List[str]], detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            field_errors=field_errors
        )


class AuthenticationException(APIException):
    """Exception for authentication errors."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(APIException):
    """Exception for authorization errors."""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )


class ResourceNotFoundException(APIException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: str = None):
        detail = f"{resource} not found"
        if identifier:
            detail += f" (ID: {identifier})"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND"
        )


class ConflictException(APIException):
    """Exception for resource conflict errors."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="RESOURCE_CONFLICT"
        )


class ServiceUnavailableException(APIException):
    """Exception for service unavailable errors."""
    
    def __init__(self, service: str, detail: str = None):
        if not detail:
            detail = f"{service} service temporarily unavailable"
        
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="SERVICE_UNAVAILABLE"
        )


class RateLimitException(APIException):
    """Exception for rate limit errors."""
    
    def __init__(self, detail: str = "Rate limit exceeded, please try again later"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED"
        )


def create_error_response(
    status_code: int,
    detail: str,
    error_code: Optional[str] = None,
    field_errors: Optional[Dict[str, List[str]]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a consistent error response format."""
    
    error_response = {
        "error": {
            "code": error_code or "UNKNOWN_ERROR",
            "message": detail,
            "status_code": status_code
        }
    }
    
    if field_errors:
        error_response["error"]["field_errors"] = field_errors
    
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    return error_response


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    
    # Log the error
    logger.error(
        f"API Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "field_errors": exc.field_errors
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=exc.error_code,
            field_errors=exc.field_errors,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors with field-specific messages."""
    
    field_errors = {}
    
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body' prefix
        if not field_path:
            field_path = "root"
        
        error_msg = error["msg"]
        error_type = error["type"]
        
        # Customize error messages based on type
        if error_type == "missing":
            error_msg = "This field is required"
        elif error_type == "string_too_short":
            error_msg = f"Must be at least {error.get('ctx', {}).get('limit_value', 1)} characters long"
        elif error_type == "string_too_long":
            error_msg = f"Must be no more than {error.get('ctx', {}).get('limit_value', 255)} characters long"
        elif error_type == "value_error.email":
            error_msg = "Must be a valid email address"
        elif error_type == "type_error.enum":
            allowed_values = error.get('ctx', {}).get('enum_values', [])
            if allowed_values:
                error_msg = f"Must be one of: {', '.join(allowed_values)}"
        elif error_type == "value_error.number.not_ge":
            error_msg = f"Must be greater than or equal to {error.get('ctx', {}).get('limit_value', 0)}"
        
        if field_path not in field_errors:
            field_errors[field_path] = []
        field_errors[field_path].append(error_msg)
    
    # Log validation error
    logger.warning(
        f"Validation Error: {request.method} {request.url.path}",
        extra={
            "field_errors": field_errors,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Input validation failed",
            error_code="VALIDATION_ERROR",
            field_errors=field_errors,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    
    # Map status codes to error codes
    error_code_map = {
        400: "BAD_REQUEST",
        401: "AUTHENTICATION_ERROR",
        403: "AUTHORIZATION_ERROR",
        404: "RESOURCE_NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "RESOURCE_CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }
    
    error_code = error_code_map.get(exc.status_code, "UNKNOWN_ERROR")
    
    # Log the error with appropriate level
    if exc.status_code >= 500:
        logger.error(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method
            }
        )
    else:
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=error_code,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database-related exceptions."""
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Database operation failed"
    error_code = "DATABASE_ERROR"
    
    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        status_code = status.HTTP_409_CONFLICT
        detail = "Data integrity constraint violation"
        error_code = "INTEGRITY_CONSTRAINT_VIOLATION"
        
        # Check for common constraint violations
        error_msg = str(exc.orig).lower()
        if "unique" in error_msg or "duplicate" in error_msg:
            if "email" in error_msg:
                detail = "Email address already exists"
            else:
                detail = "Duplicate entry detected"
    
    # Log database error
    logger.error(
        f"Database Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            status_code=status_code,
            detail=detail,
            error_code=error_code,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def openai_exception_handler(request: Request, exc: Union[RateLimitError, APIError, APIConnectionError]) -> JSONResponse:
    """Handle OpenAI API exceptions."""
    
    if isinstance(exc, RateLimitError):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        detail = "AI service rate limit exceeded, please try again later"
        error_code = "AI_RATE_LIMIT_EXCEEDED"
    elif isinstance(exc, APIConnectionError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        detail = "AI service temporarily unavailable"
        error_code = "AI_SERVICE_UNAVAILABLE"
    else:  # APIError
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        detail = "AI service error occurred"
        error_code = "AI_SERVICE_ERROR"
    
    # Log OpenAI error
    logger.error(
        f"OpenAI Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            status_code=status_code,
            detail=detail,
            error_code=error_code,
            request_id=getattr(request.state, "request_id", None)
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    
    # Log the unexpected error with full traceback
    logger.critical(
        f"Unexpected Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
            error_code="INTERNAL_SERVER_ERROR",
            request_id=getattr(request.state, "request_id", None)
        )
    )