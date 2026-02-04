from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from api.core.database import get_db
from api.core.security import verify_token
from api.models.user import User, UserRole
from api.schemas.user import TokenData

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to failed login attempts"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_role(required_role: UserRole):
    """Dependency to require a specific role."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == UserRole.SUPERADMIN:
            return current_user
        
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role"
            )
        return current_user
    return role_checker


async def require_staff_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be staff or superadmin."""
    if current_user.role not in [UserRole.STAFF, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires staff or admin privileges"
        )
    return current_user


async def require_superadmin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be superadmin."""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires superadmin privileges"
        )
    return current_user


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for optional auth)."""
    skip_dependency = getattr(SkipDependencyOverride, "skip_dependencies", False)
    if skip_dependency:
        return None
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    return user
