"""Logging middleware for TB Coin Engine ML

This module provides:
- Structured request/response logging
- Request ID tracking
- Performance metrics logging
- Error logging with context
"""
import json
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("tbcoin.api")


class RequestLogger:
    """Structured request logger
    
    Provides consistent log formatting for requests with
    contextual information for debugging and monitoring.
    """
    
    def __init__(self, name: str = "tbcoin.api"):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **context):
        """Log info message with context"""
        self._log(logging.INFO, message, context)
    
    def warning(self, message: str, **context):
        """Log warning message with context"""
        self._log(logging.WARNING, message, context)
    
    def error(self, message: str, **context):
        """Log error message with context"""
        self._log(logging.ERROR, message, context)
    
    def debug(self, message: str, **context):
        """Log debug message with context"""
        self._log(logging.DEBUG, message, context)
    
    def _log(self, level: int, message: str, context: dict):
        """Internal log method with JSON context"""
        if context:
            # Filter sensitive data
            safe_context = self._filter_sensitive(context)
            log_message = f"{message} | {json.dumps(safe_context)}"
        else:
            log_message = message
        
        self.logger.log(level, log_message)
    
    def _filter_sensitive(self, context: dict) -> dict:
        """Remove sensitive data from log context"""
        sensitive_keys = {
            "password", "secret", "token", "api_key", "apikey",
            "authorization", "cookie", "session"
        }
        
        filtered = {}
        for key, value in context.items():
            lower_key = key.lower()
            if any(s in lower_key for s in sensitive_keys):
                filtered[key] = "[REDACTED]"
            elif isinstance(value, dict):
                filtered[key] = self._filter_sensitive(value)
            else:
                filtered[key] = value
        
        return filtered


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for request/response tracking
    
    Logs all requests with:
    - Unique request ID
    - Request method and path
    - Response status code
    - Request duration
    """
    
    def __init__(self, app, logger_name: str = "tbcoin.api"):
        super().__init__(app)
        self.request_logger = RequestLogger(logger_name)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response"""
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Store in request state for access in other middlewares
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        self.request_logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            query=str(request.url.query) if request.url.query else None,
            client_ip=self._get_client_ip(request),
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            self.request_logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.request_logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                path=str(request.url.path),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class RequestLogMiddleware(BaseHTTPMiddleware):
    """Detailed request logging middleware
    
    Provides more detailed logging including:
    - Request headers (filtered)
    - Request body (for debugging)
    - Response body (optional)
    """
    
    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_length: int = 1000,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_length = max_body_length
        self.request_logger = RequestLogger("tbcoin.api.detail")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Detailed request/response logging"""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
        
        # Log request details
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "headers": self._filter_headers(dict(request.headers)),
        }
        
        # Optionally log request body
        if self.log_request_body and request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8", errors="replace")
                    log_data["request_body"] = body_str[:self.max_body_length]
                    if len(body_str) > self.max_body_length:
                        log_data["request_body"] += "...[truncated]"
            except Exception:
                pass
        
        self.request_logger.debug("Request details", **log_data)
        
        # Process request
        response = await call_next(request)
        
        # Log response details
        response_log = {
            "request_id": request_id,
            "status_code": response.status_code,
            "headers": self._filter_headers(dict(response.headers)),
        }
        
        self.request_logger.debug("Response details", **response_log)
        
        return response
    
    def _filter_headers(self, headers: dict) -> dict:
        """Filter sensitive headers"""
        sensitive = {"authorization", "cookie", "x-api-key", "x-auth-token"}
        return {
            k: "[REDACTED]" if k.lower() in sensitive else v
            for k, v in headers.items()
        }


class PerformanceLogger:
    """Performance metrics logger
    
    Tracks and logs performance metrics for monitoring.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("tbcoin.performance")
        self._metrics = {}
    
    def record_timing(self, operation: str, duration_ms: float):
        """Record operation timing"""
        if operation not in self._metrics:
            self._metrics[operation] = {
                "count": 0,
                "total_ms": 0,
                "min_ms": float("inf"),
                "max_ms": 0,
            }
        
        metrics = self._metrics[operation]
        metrics["count"] += 1
        metrics["total_ms"] += duration_ms
        metrics["min_ms"] = min(metrics["min_ms"], duration_ms)
        metrics["max_ms"] = max(metrics["max_ms"], duration_ms)
        
        # Log slow operations
        if duration_ms > 1000:  # > 1 second
            self.logger.warning(
                f"Slow operation: {operation} took {duration_ms:.2f}ms"
            )
    
    def get_metrics(self) -> dict:
        """Get aggregated performance metrics"""
        result = {}
        for operation, metrics in self._metrics.items():
            if metrics["count"] > 0:
                result[operation] = {
                    "count": metrics["count"],
                    "avg_ms": round(metrics["total_ms"] / metrics["count"], 2),
                    "min_ms": round(metrics["min_ms"], 2),
                    "max_ms": round(metrics["max_ms"], 2),
                }
        return result


# Global performance logger instance
performance_logger = PerformanceLogger()
