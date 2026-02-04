from fastapi import Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

from api.models.audit_log import AuditLog, AuditAction
from api.models.user import User
from api.core.log_sanitizer import sanitize_dict

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit logging service for tracking user actions.
    
    All significant actions should be logged for:
    - Compliance (GDPR, data protection)
    - Security monitoring
    - Incident investigation
    - User activity tracking
    """
    
    @staticmethod
    def log(
        db: Session,
        action: AuditAction,
        success: str = "success",
        user: Optional[User] = None,
        tenant_id: Optional[int] = None,
        tenant_slug: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            action: Action being performed (AuditAction enum)
            success: Outcome (success, failure, error)
            user: User performing the action (if authenticated)
            tenant_id: Tenant context
            tenant_slug: Tenant slug (denormalized)
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            description: Human-readable description
            metadata: Additional context (will be sanitized)
            request: FastAPI request object
            error_message: Error message if failed
            
        Returns:
            Created AuditLog entry
        """
        # Extract request context
        ip_address = None
        user_agent = None
        request_path = None
        request_method = None
        
        if request:
            # Get IP address (handle proxy headers)
            ip_address = request.headers.get("X-Forwarded-For")
            if ip_address:
                ip_address = ip_address.split(",")[0].strip()
            else:
                ip_address = request.client.host if request.client else None
            
            user_agent = request.headers.get("User-Agent")
            request_path = str(request.url.path)
            request_method = request.method
        
        # Sanitize metadata to remove sensitive data
        sanitized_metadata = None
        if metadata:
            sanitized_metadata = sanitize_dict(metadata)
        
        # Create audit log entry
        audit_entry = AuditLog(
            timestamp=datetime.now(timezone.utc),
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            tenant_id=tenant_id,
            tenant_slug=tenant_slug,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            meta=sanitized_metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            success=success,
            error_message=error_message,
        )
        
        try:
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            
            # Also log to application logger for real-time monitoring
            log_message = f"AUDIT: {action.value} by user_id={user.id if user else 'anonymous'}"
            if tenant_slug:
                log_message += f" tenant={tenant_slug}"
            if resource_type and resource_id:
                log_message += f" {resource_type}={resource_id}"
            log_message += f" result={success}"
            
            if success == "success":
                logger.info(log_message)
            else:
                logger.warning(log_message)
            
            return audit_entry
            
        except Exception as e:
            # Audit logging should never break the application
            logger.error(f"Failed to create audit log: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def log_auth_event(
        db: Session,
        action: AuditAction,
        email: str,
        success: str = "success",
        request: Optional[Request] = None,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        Log authentication-related events.
        
        Args:
            db: Database session
            action: Authentication action
            email: User email
            success: Outcome
            request: Request object
            error_message: Error message if failed
        """
        return AuditLogger.log(
            db=db,
            action=action,
            success=success,
            user=None,  # User not authenticated yet
            description=f"Authentication attempt for {email}",
            metadata={"email": email},
            request=request,
            error_message=error_message,
        )
    
    @staticmethod
    def log_data_access(
        db: Session,
        user: User,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        tenant_slug: Optional[str] = None,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log data access events (views, exports).
        
        Important for GDPR compliance and security monitoring.
        """
        return AuditLogger.log(
            db=db,
            action=action,
            user=user,
            tenant_id=tenant_id,
            tenant_slug=tenant_slug,
            resource_type=resource_type,
            resource_id=resource_id,
            description=f"Data access: {resource_type}",
            metadata=metadata,
            request=request,
        )
    
    @staticmethod
    def log_security_event(
        db: Session,
        action: AuditAction,
        description: str,
        user: Optional[User] = None,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log security-related events (unauthorized access, rate limits, etc.).
        
        These are high-priority events that may require investigation.
        """
        return AuditLogger.log(
            db=db,
            action=action,
            success="failure",
            user=user,
            description=description,
            metadata=metadata,
            request=request,
        )


def get_audit_logger() -> AuditLogger:
    """Dependency for getting audit logger."""
    return AuditLogger()
