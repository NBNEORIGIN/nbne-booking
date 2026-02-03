from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from api.core.database import get_db
from api.core.auth import get_current_user
from api.core.permissions import require_admin_access
from api.core.audit import AuditLogger
from api.models.user import User
from api.models.booking import Booking
from api.models.audit_log import AuditLog, AuditAction
from pydantic import BaseModel, EmailStr


router = APIRouter()


class DSARRequest(BaseModel):
    """Data Subject Access Request."""
    email: EmailStr


class DSARResponse(BaseModel):
    """DSAR response with user's personal data."""
    request_id: str
    timestamp: datetime
    user_data: Dict[str, Any]
    bookings: list
    audit_logs: list


class DataDeletionRequest(BaseModel):
    """Request to delete user data."""
    email: EmailStr
    confirmation: str  # Must be "DELETE"


@router.post("/dsar", response_model=DSARResponse)
async def data_subject_access_request(
    request: DSARRequest,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Data Subject Access Request (DSAR) - GDPR Article 15.
    
    Returns all personal data held about a user.
    Admin only to prevent unauthorized data access.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for this email address"
        )
    
    # Collect user data
    user_data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "tenant_id": user.tenant_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }
    
    # Collect bookings where user is the customer
    bookings = db.query(Booking).filter(
        Booking.customer_email == request.email
    ).all()
    
    bookings_data = [
        {
            "id": booking.id,
            "service_id": booking.service_id,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "customer_name": booking.customer_name,
            "customer_email": booking.customer_email,
            "customer_phone": booking.customer_phone,
            "status": booking.status.value,
            "notes": booking.notes,
            "created_at": booking.created_at.isoformat(),
        }
        for booking in bookings
    ]
    
    # Collect audit logs
    audit_logs = db.query(AuditLog).filter(
        AuditLog.user_id == user.id
    ).order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    audit_logs_data = [
        {
            "timestamp": log.timestamp.isoformat(),
            "action": log.action,
            "description": log.description,
            "ip_address": log.ip_address,
        }
        for log in audit_logs
    ]
    
    # Generate request ID
    request_id = f"DSAR-{user.id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    
    # Audit log the DSAR
    AuditLogger.log(
        db=db,
        action=AuditAction.DATA_EXPORT,
        user=current_user,
        resource_type="user",
        resource_id=user.id,
        description=f"DSAR executed for {request.email}",
        metadata={"request_id": request_id, "target_email": request.email}
    )
    
    return DSARResponse(
        request_id=request_id,
        timestamp=datetime.now(timezone.utc),
        user_data=user_data,
        bookings=bookings_data,
        audit_logs=audit_logs_data
    )


@router.post("/delete-user-data")
async def delete_user_data(
    request: DataDeletionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Delete or anonymize user data - GDPR Article 17 (Right to Erasure).
    
    Strategy:
    - User account: Anonymize (keep for referential integrity)
    - Bookings: Anonymize customer data
    - Audit logs: Keep (legal requirement for 2 years)
    
    Requires confirmation string "DELETE" to prevent accidents.
    """
    if request.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation string must be 'DELETE'"
        )
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Anonymize user account
    anonymized_email = f"deleted-user-{user.id}@anonymized.local"
    user.email = anonymized_email
    user.full_name = f"Deleted User {user.id}"
    user.hashed_password = "DELETED"
    user.is_active = False
    user.is_verified = False
    
    # Anonymize bookings
    bookings = db.query(Booking).filter(
        Booking.customer_email == request.email
    ).all()
    
    for booking in bookings:
        booking.customer_name = f"Deleted Customer {booking.id}"
        booking.customer_email = f"deleted-{booking.id}@anonymized.local"
        booking.customer_phone = None
        booking.notes = "[Customer data deleted per GDPR request]"
    
    db.commit()
    
    # Audit log the deletion
    AuditLogger.log(
        db=db,
        action=AuditAction.DATA_DELETE,
        user=current_user,
        resource_type="user",
        resource_id=user.id,
        description=f"User data deleted/anonymized for {request.email}",
        metadata={
            "original_email": request.email,
            "bookings_anonymized": len(bookings)
        }
    )
    
    return {
        "status": "success",
        "message": f"User data anonymized for {request.email}",
        "user_id": user.id,
        "bookings_anonymized": len(bookings),
        "audit_logs_retained": "Audit logs retained per legal requirements"
    }


@router.get("/retention-status")
async def get_retention_status(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get data retention status.
    
    Shows counts of records that may be eligible for deletion
    based on retention policies.
    """
    from datetime import timedelta
    
    # Count old audit logs (>2 years)
    two_years_ago = datetime.now(timezone.utc) - timedelta(days=730)
    old_audit_logs = db.query(AuditLog).filter(
        AuditLog.timestamp < two_years_ago
    ).count()
    
    # Count inactive users (>1 year no login)
    one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
    inactive_users = db.query(User).filter(
        User.last_login < one_year_ago
    ).count()
    
    # Count old bookings (>2 years)
    old_bookings = db.query(Booking).filter(
        Booking.created_at < two_years_ago
    ).count()
    
    return {
        "audit_logs_older_than_2_years": old_audit_logs,
        "users_inactive_1_year": inactive_users,
        "bookings_older_than_2_years": old_bookings,
        "retention_policy": {
            "audit_logs": "2 years",
            "user_accounts": "Indefinite (anonymize on request)",
            "bookings": "2 years (anonymize after)"
        }
    }
