"""Authentication middleware for TB Coin Engine ML

This module provides:
- JWT authentication with configurable expiry
- API key authentication
- Role-based access control (RBAC)
- User session management
"""
import logging
from datetime import datetime, timedelta
from typing import Annotated, Callable, List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.schemas import TokenData, User, UserRole, UserInDB

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class JWTAuth:
    """JWT Authentication handler
    
    Provides methods for creating and verifying JWT tokens
    following security best practices.
    """
    
    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        self.secret_key = secret_key or settings.JWT_SECRET_KEY
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token
        
        Args:
            data: Token payload data
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token
        
        Args:
            data: Token payload data
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            sub: str = payload.get("sub")
            role: str = payload.get("role", "user")
            
            if sub is None:
                return None
            
            return TokenData(
                sub=sub,
                role=UserRole(role) if role else UserRole.USER,
                exp=datetime.fromtimestamp(payload.get("exp", 0))
            )
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hashed password
            
        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Bcrypt hashed password
        """
        return pwd_context.hash(password)


class APIKeyAuth:
    """API Key Authentication handler
    
    Provides simple API key validation for service-to-service
    authentication.
    """
    
    def __init__(self, valid_keys: Optional[List[str]] = None):
        self.valid_keys = valid_keys or []
        # Add default API key from settings
        if settings.API_KEY:
            self.valid_keys.append(settings.API_KEY)
    
    def verify_key(self, api_key: str) -> bool:
        """Verify an API key
        
        Args:
            api_key: API key to verify
            
        Returns:
            True if key is valid
        """
        return api_key in self.valid_keys
    
    def add_key(self, api_key: str) -> None:
        """Add a valid API key
        
        Args:
            api_key: API key to add
        """
        if api_key not in self.valid_keys:
            self.valid_keys.append(api_key)
    
    def remove_key(self, api_key: str) -> None:
        """Remove an API key
        
        Args:
            api_key: API key to remove
        """
        if api_key in self.valid_keys:
            self.valid_keys.remove(api_key)


# Global authentication instances
jwt_auth = JWTAuth()
api_key_auth = APIKeyAuth()


# In-memory user store (replace with database in production)
_users_db: dict = {}


async def get_user(user_id: str) -> Optional[UserInDB]:
    """Get user from database
    
    Args:
        user_id: User identifier
        
    Returns:
        User if found, None otherwise
    """
    # TODO: Replace with actual database lookup
    return _users_db.get(user_id)


async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User if authenticated, None otherwise
    """
    user = await get_user(username)
    if not user:
        return None
    if not jwt_auth.verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials],
        Depends(bearer_scheme)
    ] = None,
    api_key: Annotated[Optional[str], Depends(api_key_header)] = None,
) -> User:
    """Get current authenticated user
    
    Supports both JWT Bearer token and API key authentication.
    
    Args:
        credentials: Bearer token credentials
        api_key: API key header value
        
    Returns:
        Authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    # Try JWT authentication first
    if credentials:
        token_data = jwt_auth.verify_token(credentials.credentials)
        if token_data:
            user = await get_user(token_data.sub)
            if user:
                return User(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at
                )
    
    # Try API key authentication
    if api_key and api_key_auth.verify_key(api_key):
        # Return a system user for API key auth
        return User(
            id="system",
            username="api_user",
            email="api@system.local",
            role=UserRole.OPERATOR,
            is_active=True
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user
    
    Verifies that the authenticated user is active.
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: List[UserRole]) -> Callable:
    """Create a dependency that requires specific roles
    
    Role-based access control (RBAC) decorator.
    
    Args:
        allowed_roles: List of roles that are allowed access
        
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    
    return role_checker


# Pre-configured role dependencies
require_admin = require_role([UserRole.ADMIN])
require_operator = require_role([UserRole.ADMIN, UserRole.OPERATOR])
require_user = require_role([UserRole.ADMIN, UserRole.OPERATOR, UserRole.USER])
