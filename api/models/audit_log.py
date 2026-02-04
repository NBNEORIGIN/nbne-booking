from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Index
from sqlalchemy.sql import func
from api.core.database import Base
import enum


class AuditAction(str, enum.Enum):
    """Audit action types for tracking user activities."""
    
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET = "password_reset"
    PASSWORD_CHANGE = "password_change"
    
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    
    # Tenant Management
    TENANT_CREATE = "tenant_create"
    TENANT_UPDATE = "tenant_update"
    TENANT_DELETE = "tenant_delete"
    
    # Booking Operations
    BOOKING_CREATE = "booking_create"
    BOOKING_UPDATE = "booking_update"
    BOOKING_CANCEL = "booking_cancel"
    BOOKING_VIEW = "booking_view"
    BOOKING_EXPORT = "booking_export"
    
    # Service Management
    SERVICE_CREATE = "service_create"
    SERVICE_UPDATE = "service_update"
    SERVICE_DELETE = "service_delete"
    
    # Data Access
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    
    # Admin Actions
    BRANDING_UPDATE = "branding_update"
    SETTINGS_UPDATE = "settings_update"
    
    # Security Events
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class AuditLog(Base):
    """
    Audit log for tracking all significant user actions.
    
    This is an append-only table for compliance and security monitoring.
    Records should never be updated or deleted (except for retention policy).
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # When
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Who
    user_id = Column(Integer, nullable=True, index=True)  # Null for unauthenticated actions
    user_email = Column(String(255), nullable=True)  # Denormalized for easier querying
    
    # Where (tenant context)
    tenant_id = Column(Integer, nullable=True, index=True)
    tenant_slug = Column(String(100), nullable=True)  # Denormalized
    
    # What
    action = Column(String(50), nullable=False, index=True)  # AuditAction enum value
    resource_type = Column(String(50), nullable=True, index=True)  # e.g., "booking", "user", "tenant"
    resource_id = Column(Integer, nullable=True)  # ID of affected resource
    
    # Details
    description = Column(Text, nullable=True)  # Human-readable description
    meta = Column(JSON, nullable=True)  # Additional context (sanitized)
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    
    # Outcome
    success = Column(String(10), nullable=False, default="success")  # success, failure, error
    error_message = Column(Text, nullable=True)  # If failed
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_audit_logs_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('ix_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_logs_action_timestamp', 'action', 'timestamp'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, timestamp={self.timestamp})>"
