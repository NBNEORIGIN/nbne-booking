from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

from api.core.database import get_db
from api.core.permissions import require_admin_access
from api.models.user import User
from api.models.audit_log import AuditLog
from pydantic import BaseModel


router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    id: int
    timestamp: datetime
    user_id: Optional[int]
    user_email: Optional[str]
    tenant_id: Optional[int]
    tenant_slug: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    description: Optional[str]
    ip_address: Optional[str]
    success: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[AuditLogResponse])
def list_audit_logs(
    skip: int = 0,
    limit: int = Query(100, le=1000),
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    tenant_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    List audit logs with filters (admin only).
    
    Supports filtering by:
    - action: Specific action type
    - user_id: User who performed action
    - tenant_id: Tenant context
    - start_date/end_date: Time range
    """
    query = db.query(AuditLog)
    
    # Apply filters
    if action:
        query = query.filter(AuditLog.action == action)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if tenant_id:
        query = query.filter(AuditLog.tenant_id == tenant_id)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    # Order by timestamp descending (most recent first)
    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    return logs


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
def get_user_audit_logs(
    user_id: int,
    days: int = Query(30, le=365),
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific user (admin only).
    
    Returns logs from the last N days (default: 30, max: 365).
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.timestamp >= start_date
    ).order_by(desc(AuditLog.timestamp)).all()
    
    return logs


@router.get("/tenant/{tenant_id}", response_model=List[AuditLogResponse])
def get_tenant_audit_logs(
    tenant_id: int,
    days: int = Query(30, le=365),
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific tenant (admin only).
    
    Returns logs from the last N days (default: 30, max: 365).
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(AuditLog).filter(
        AuditLog.tenant_id == tenant_id,
        AuditLog.timestamp >= start_date
    ).order_by(desc(AuditLog.timestamp)).all()
    
    return logs


@router.get("/security-events", response_model=List[AuditLogResponse])
def get_security_events(
    days: int = Query(7, le=90),
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get security-related audit logs (admin only).
    
    Includes:
    - Failed logins
    - Unauthorized access attempts
    - Permission denied events
    - Rate limit exceeded
    
    Returns logs from the last N days (default: 7, max: 90).
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    security_actions = [
        'login_failed',
        'unauthorized_access',
        'permission_denied',
        'rate_limit_exceeded'
    ]
    
    logs = db.query(AuditLog).filter(
        AuditLog.action.in_(security_actions),
        AuditLog.timestamp >= start_date
    ).order_by(desc(AuditLog.timestamp)).all()
    
    return logs
