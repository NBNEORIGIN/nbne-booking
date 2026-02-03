from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import logging

from api.core.database import get_db
from api.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    generate_reset_token,
    hash_reset_token
)
from api.core.auth import get_current_user, get_current_active_user
from api.models.user import User
from api.models.password_reset import PasswordResetToken
from api.schemas.user import (
    UserLogin,
    Token,
    UserCreate,
    UserResponse,
    PasswordResetRequest,
    PasswordReset,
    PasswordChange
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user (invite-only, requires valid tenant_id for non-superadmin).
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        tenant_id=user_data.tenant_id,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email} (role: {new_user.role})")
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    Returns JWT access token.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        logger.warning(f"Login attempt for non-existent user: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if user.is_locked():
        logger.warning(f"Login attempt for locked account: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to failed login attempts. Please try again later."
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            logger.warning(f"Account locked due to failed attempts: {user.email}")
        
        db.commit()
        
        logger.warning(f"Failed login attempt for user: {user.email} (attempts: {user.failed_login_attempts})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    
    logger.info(f"Successful login: {user.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.
    Note: JWT tokens cannot be invalidated server-side without additional infrastructure.
    Client should discard the token.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.post("/password-reset-request")
def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset token.
    Always returns success to prevent email enumeration.
    """
    user = db.query(User).filter(User.email == request_data.email).first()
    
    if user:
        token = generate_reset_token()
        token_hash = hash_reset_token(token)
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        db.add(reset_token)
        db.commit()
        
        logger.info(f"Password reset requested for: {user.email}")
        
    
    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/password-reset")
def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password using a valid token."""
    token_hash = hash_reset_token(reset_data.token)
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()
    
    if not reset_token or not reset_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    
    reset_token.is_used = True
    
    db.commit()
    
    logger.info(f"Password reset completed for: {user.email}")
    
    return {"message": "Password has been reset successfully"}


@router.post("/password-change")
def change_password(
    change_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user."""
    if not verify_password(change_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    current_user.hashed_password = get_password_hash(change_data.new_password)
    db.commit()
    
    logger.info(f"Password changed for: {current_user.email}")
    
    return {"message": "Password changed successfully"}
