"""Security middleware for TB Coin Engine ML

This module provides:
- Rate limiting
- Security headers
- Input sanitization
- Request validation
"""
import logging
import re
import time
from typing import Callable, Dict, Optional
import html

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware
    
    Limits the number of requests per client to prevent abuse.
    Uses in-memory storage by default (use Redis in production).
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_second: int = 10,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_second
        self._request_counts: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        client_id = self._get_client_id(request)
        
        if not self._check_rate_limit(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Prefer API key for identification
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key[:8]}..."
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        
        # Initialize or get request timestamps
        if client_id not in self._request_counts:
            self._request_counts[client_id] = []
        
        timestamps = self._request_counts[client_id]
        
        # Remove old timestamps (older than 1 minute)
        timestamps = [ts for ts in timestamps if now - ts < 60]
        self._request_counts[client_id] = timestamps
        
        # Check per-second limit
        recent_second = len([ts for ts in timestamps if now - ts < 1])
        if recent_second >= self.requests_per_second:
            return False
        
        # Check per-minute limit
        if len(timestamps) >= self.requests_per_minute:
            return False
        
        # Record this request
        timestamps.append(now)
        self._request_counts[client_id] = timestamps
        
        return True


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware
    
    Adds security headers to all responses to protect against
    common web vulnerabilities.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "frame-ancestors 'none'"
        )
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Clickjacking protection
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HTTPS enforcement
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Input sanitization middleware
    
    Sanitizes user input to prevent:
    - Cross-site scripting (XSS)
    - SQL injection patterns
    - NoSQL injection patterns
    """
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(\bAND\b\s+\d+\s*=\s*\d+)",
        r"('.*--)",
    ]
    
    # NoSQL injection patterns
    NOSQL_PATTERNS = [
        r"(\$where|\$gt|\$lt|\$ne|\$regex|\$or|\$and)",
        r"(\{.*\}.*\:.*\{)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(on\w+\s*=)",
        r"(<iframe[^>]*>)",
        r"(<object[^>]*>)",
        r"(<embed[^>]*>)",
    ]
    
    def __init__(self, app, strict_mode: bool = False):
        super().__init__(app)
        self.strict_mode = strict_mode
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        self.sql_regex = [
            re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS
        ]
        self.nosql_regex = [
            re.compile(p, re.IGNORECASE) for p in self.NOSQL_PATTERNS
        ]
        self.xss_regex = [
            re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Sanitize request input"""
        # Check query parameters
        query_string = str(request.url.query)
        if query_string:
            self._check_injection(query_string, "query parameters")
        
        # Check path parameters
        path = str(request.url.path)
        self._check_injection(path, "path")
        
        # Check headers (selected ones)
        for header in ["Referer", "User-Agent", "Origin"]:
            value = request.headers.get(header)
            if value:
                self._check_xss(value, f"header {header}")
        
        response = await call_next(request)
        return response
    
    def _check_injection(self, value: str, source: str) -> None:
        """Check for injection patterns"""
        # Check SQL injection
        for pattern in self.sql_regex:
            if pattern.search(value):
                logger.warning(f"Potential SQL injection in {source}: {value[:100]}")
                if self.strict_mode:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid input detected"
                    )
        
        # Check NoSQL injection
        for pattern in self.nosql_regex:
            if pattern.search(value):
                logger.warning(f"Potential NoSQL injection in {source}: {value[:100]}")
                if self.strict_mode:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid input detected"
                    )
        
        # Check XSS
        self._check_xss(value, source)
    
    def _check_xss(self, value: str, source: str) -> None:
        """Check for XSS patterns"""
        for pattern in self.xss_regex:
            if pattern.search(value):
                logger.warning(f"Potential XSS in {source}: {value[:100]}")
                if self.strict_mode:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid input detected"
                    )
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize a string value
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return value
        
        # HTML escape to prevent XSS
        sanitized = html.escape(value)
        
        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")
        
        # Remove potential script tags (double protection)
        sanitized = re.sub(r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @staticmethod
    def sanitize_dict(data: dict) -> dict:
        """Recursively sanitize dictionary values
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            clean_key = InputSanitizationMiddleware.sanitize_string(str(key))
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = InputSanitizationMiddleware.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = InputSanitizationMiddleware.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    InputSanitizationMiddleware.sanitize_dict(v) if isinstance(v, dict)
                    else InputSanitizationMiddleware.sanitize_string(v) if isinstance(v, str)
                    else v
                    for v in value
                ]
            else:
                sanitized[clean_key] = value
        
        return sanitized


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Request validation middleware
    
    Validates incoming requests for:
    - Content type
    - Content length
    - Required headers
    """
    
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    
    def __init__(self, app, max_content_length: int = None):
        super().__init__(app)
        self.max_content_length = max_content_length or self.MAX_CONTENT_LENGTH
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request"""
        # Check content length
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_content_length:
                    raise HTTPException(
                        status_code=413,
                        detail="Request payload too large"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Content-Length header"
                )
        
        # Validate content type for POST/PUT/PATCH
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("Content-Type", "")
            if content_type and not self._is_valid_content_type(content_type):
                logger.warning(f"Invalid content type: {content_type}")
        
        response = await call_next(request)
        return response
    
    def _is_valid_content_type(self, content_type: str) -> bool:
        """Check if content type is valid"""
        valid_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ]
        return any(ct in content_type for ct in valid_types)
