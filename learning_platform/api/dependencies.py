"""Database and authentication dependencies."""
from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

from learning_platform.models.base import get_session
from learning_platform.models.user import User

# Security scheme
security = HTTPBearer(auto_error=False)

# JWT settings (should be in config in production)
JWT_SECRET = "learning-platform-secret-key"  # Should be from environment
JWT_ALGORITHM = "HS256"


def get_db() -> Generator:
    """Get database session."""
    SessionLocal = get_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def decode_token(token: str) -> Optional[dict]:
    """Decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current authenticated user."""
    if not credentials:
        return None
    
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require authentication."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def create_access_token(user_id: int, expires_hours: int = 24) -> str:
    """Create a JWT access token."""
    from datetime import timedelta
    
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
