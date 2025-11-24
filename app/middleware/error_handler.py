"""Error handling middleware for TB Coin Engine ML

This module provides:
- Comprehensive error handling
- Structured error responses
- Error logging with context
- Custom exception classes
"""
import logging
import traceback
from typing import Callable, Optional, Union

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.schemas import ErrorResponse, ErrorDetail

logger = logging.getLogger("tbcoin.errors")


# ============================================================================
# Custom Exception Classes
# ============================================================================

class TBCoinException(Exception):
    """Base exception for TB Coin Engine"""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[list] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class ValidationException(TBCoinException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[list] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class AuthenticationException(TBCoinException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
        )


class AuthorizationException(TBCoinException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
        )


class NotFoundException(TBCoinException):
    """Resource not found exception"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
        )


class ConflictException(TBCoinException):
    """Resource conflict exception"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
        )


class RateLimitException(TBCoinException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class ServiceUnavailableException(TBCoinException):
    """Service unavailable exception"""
    
    def __init__(self, service: str, message: str = None):
        super().__init__(
            message=message or f"{service} is currently unavailable",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


class DatabaseException(TBCoinException):
    """Database error exception"""
    
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
        )


# ============================================================================
# Error Handler Middleware
# ============================================================================

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware
    
    Catches all exceptions and returns consistent error responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Handle errors in request processing"""
        request_id = getattr(request.state, "request_id", None)
        
        try:
            response = await call_next(request)
            return response
            
        except TBCoinException as e:
            return self._handle_tbcoin_exception(e, request_id)
            
        except HTTPException as e:
            return self._handle_http_exception(e, request_id)
            
        except RequestValidationError as e:
            return self._handle_validation_error(e, request_id)
            
        except ValidationError as e:
            return self._handle_pydantic_error(e, request_id)
            
        except Exception as e:
            return self._handle_unexpected_error(e, request_id)
    
    def _handle_tbcoin_exception(
        self,
        exc: TBCoinException,
        request_id: Optional[str]
    ) -> JSONResponse:
        """Handle custom TB Coin exceptions"""
        logger.warning(
            f"TBCoin exception: {exc.code} - {exc.message}",
            extra={"request_id": request_id}
        )
        
        error_response = ErrorResponse(
            message=exc.message,
            details=[
                ErrorDetail(code=exc.code, message=d) if isinstance(d, str)
                else ErrorDetail(**d) if isinstance(d, dict)
                else d
                for d in exc.details
            ] if exc.details else None,
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )
    
    def _handle_http_exception(
        self,
        exc: HTTPException,
        request_id: Optional[str]
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={"request_id": request_id}
        )
        
        error_response = ErrorResponse(
            message=str(exc.detail),
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )
    
    def _handle_validation_error(
        self,
        exc: RequestValidationError,
        request_id: Optional[str]
    ) -> JSONResponse:
        """Handle request validation errors"""
        logger.warning(
            f"Validation error: {len(exc.errors())} error(s)",
            extra={"request_id": request_id}
        )
        
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            details.append(ErrorDetail(
                code="VALIDATION_ERROR",
                message=error.get("msg", "Invalid value"),
                field=field if field else None,
            ))
        
        error_response = ErrorResponse(
            message="Request validation failed",
            details=details,
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )
    
    def _handle_pydantic_error(
        self,
        exc: ValidationError,
        request_id: Optional[str]
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""
        logger.warning(
            f"Pydantic validation error: {len(exc.errors())} error(s)",
            extra={"request_id": request_id}
        )
        
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            details.append(ErrorDetail(
                code="VALIDATION_ERROR",
                message=error.get("msg", "Invalid value"),
                field=field if field else None,
            ))
        
        error_response = ErrorResponse(
            message="Data validation failed",
            details=details,
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )
    
    def _handle_unexpected_error(
        self,
        exc: Exception,
        request_id: Optional[str]
    ) -> JSONResponse:
        """Handle unexpected errors"""
        # Log full traceback for debugging
        logger.error(
            f"Unexpected error: {type(exc).__name__} - {str(exc)}",
            extra={"request_id": request_id, "traceback": traceback.format_exc()}
        )
        
        # Don't expose internal error details to clients
        error_response = ErrorResponse(
            message="An unexpected error occurred. Please try again later.",
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )


def error_handler(app: FastAPI) -> None:
    """Register error handlers with FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(TBCoinException)
    async def tbcoin_exception_handler(
        request: Request,
        exc: TBCoinException
    ) -> JSONResponse:
        """Handle TBCoin exceptions"""
        request_id = getattr(request.state, "request_id", None)
        
        error_response = ErrorResponse(
            message=exc.message,
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation exceptions"""
        request_id = getattr(request.state, "request_id", None)
        
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            details.append(ErrorDetail(
                code="VALIDATION_ERROR",
                message=error.get("msg", "Invalid value"),
                field=field if field else None,
            ))
        
        error_response = ErrorResponse(
            message="Request validation failed",
            details=details,
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle all unhandled exceptions"""
        request_id = getattr(request.state, "request_id", None)
        
        logger.error(
            f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
            extra={"request_id": request_id, "traceback": traceback.format_exc()}
        )
        
        error_response = ErrorResponse(
            message="An unexpected error occurred",
            request_id=request_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode="json", exclude_none=True),
        )
