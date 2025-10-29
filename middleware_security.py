# middleware/security.py
from fastapi import Request, HTTPException
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
import time
import redis.asyncio as redis
from typing import Dict, List
import logging

class RateLimitMiddleware:
    def __init__(self, redis_client: redis.Redis, requests_per_minute: int = 60):
        self.redis = redis_client
        self.requests_per_minute = requests_per_minute
        
    async def __call__(self, request: Request, call_next):
        # Get client identifier (API key or IP)
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        if not await self._check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier from request"""
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        return f"ip:{request.client.host}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        key = f"rate_limit:{client_id}"
        current = await self.redis.get(key)
        
        if current and int(current) >= self.requests_per_minute:
            return False
            
        async with self.redis.pipeline() as pipe:
            pipe.incr(key, 1)
            pipe.expire(key, 60)  # Reset every minute
            results = await pipe.execute()
            
        return True

class SecurityHeadersMiddleware:
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

# CORS configuration
def setup_cors():
    return CORSMiddleware(
        app,
        allow_origins=["https://tbcoin.com", "https://app.tbcoin.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )