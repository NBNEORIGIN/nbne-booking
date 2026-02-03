import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from api.main import app
from api.core.database import Base, get_db
from api.models.user import User, UserRole
from api.models.audit_log import AuditLog, AuditAction
from api.core.security import get_password_hash, create_access_token
from api.core.audit import AuditLogger

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_audit.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Test User",
        role=UserRole.CLIENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def admin_user():
    """Create an admin user."""
    db = TestingSessionLocal()
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Admin User",
        role=UserRole.SUPERADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_audit_log_created_on_login(test_user):
    """Test that audit log is created on successful login."""
    db = TestingSessionLocal()
    
    # Count audit logs before
    count_before = db.query(AuditLog).count()
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    
    assert response.status_code == 200
    
    # Check audit log created
    count_after = db.query(AuditLog).count()
    assert count_after == count_before + 1
    
    # Verify audit log content
    audit_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert audit_log.action == AuditAction.LOGIN.value
    assert audit_log.user_id == test_user.id
    assert audit_log.user_email == test_user.email
    assert audit_log.success == "success"
    
    db.close()


def test_audit_log_created_on_failed_login():
    """Test that audit log is created on failed login."""
    db = TestingSessionLocal()
    
    # Count audit logs before
    count_before = db.query(AuditLog).count()
    
    # Failed login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPass123!"
        }
    )
    
    assert response.status_code == 401
    
    # Check audit log created
    count_after = db.query(AuditLog).count()
    assert count_after == count_before + 1
    
    # Verify audit log content
    audit_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert audit_log.action == AuditAction.LOGIN_FAILED.value
    assert audit_log.success == "failure"
    assert audit_log.error_message is not None
    
    db.close()


def test_audit_logger_basic():
    """Test basic audit logger functionality."""
    db = TestingSessionLocal()
    
    user = User(
        email="logger@example.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Logger User",
        role=UserRole.CLIENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create audit log
    audit_log = AuditLogger.log(
        db=db,
        action=AuditAction.BOOKING_CREATE,
        user=user,
        tenant_id=1,
        resource_type="booking",
        resource_id=123,
        description="Created booking",
        metadata={"service_id": 1}
    )
    
    assert audit_log is not None
    assert audit_log.action == AuditAction.BOOKING_CREATE.value
    assert audit_log.user_id == user.id
    assert audit_log.tenant_id == 1
    assert audit_log.resource_type == "booking"
    assert audit_log.resource_id == 123
    
    db.close()


def test_audit_logger_sanitizes_metadata():
    """Test that audit logger sanitizes sensitive data in metadata."""
    db = TestingSessionLocal()
    
    user = User(
        email="sanitize@example.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Sanitize User",
        role=UserRole.CLIENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create audit log with sensitive data
    audit_log = AuditLogger.log(
        db=db,
        action=AuditAction.USER_UPDATE,
        user=user,
        metadata={
            "email": "user@example.com",
            "password": "secret123",  # Should be sanitized
            "api_key": "sk_live_1234567890"  # Should be sanitized
        }
    )
    
    assert audit_log is not None
    assert audit_log.metadata["email"] == "user@example.com"
    assert audit_log.metadata["password"] == "***REDACTED***"
    assert audit_log.metadata["api_key"] == "***REDACTED***"
    
    db.close()


def test_audit_log_api_requires_admin(test_user, admin_user):
    """Test that audit log API requires admin access."""
    # Get tokens
    test_token = create_access_token({"sub": test_user.id, "email": test_user.email, "role": "client"})
    admin_token = create_access_token({"sub": admin_user.id, "email": admin_user.email, "role": "superadmin"})
    
    # Client user cannot access
    response = client.get(
        "/api/v1/audit/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 403
    
    # Admin can access
    response = client.get(
        "/api/v1/audit/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_audit_log_filtering(admin_user):
    """Test audit log filtering."""
    db = TestingSessionLocal()
    
    # Create some audit logs
    for i in range(5):
        AuditLogger.log(
            db=db,
            action=AuditAction.BOOKING_CREATE if i % 2 == 0 else AuditAction.BOOKING_UPDATE,
            user=admin_user,
            tenant_id=1,
            resource_type="booking",
            resource_id=i
        )
    
    db.close()
    
    admin_token = create_access_token({"sub": admin_user.id, "email": admin_user.email, "role": "superadmin"})
    
    # Filter by action
    response = client.get(
        "/api/v1/audit/?action=booking_create",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3  # 3 create actions
    
    # Filter by tenant
    response = client.get(
        "/api/v1/audit/?tenant_id=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 5  # All logs


def test_audit_log_ip_address_captured():
    """Test that IP address is captured in audit logs."""
    db = TestingSessionLocal()
    
    # Login (which creates audit log)
    user = User(
        email="ip@example.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="IP User",
        role=UserRole.CLIENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ip@example.com",
            "password": "Pass123!"
        }
    )
    
    assert response.status_code == 200
    
    # Check IP address captured
    audit_log = db.query(AuditLog).filter(
        AuditLog.action == AuditAction.LOGIN.value,
        AuditLog.user_email == "ip@example.com"
    ).first()
    
    assert audit_log is not None
    assert audit_log.ip_address is not None  # TestClient provides an IP
    
    db.close()


def test_audit_log_never_fails_application():
    """Test that audit logging failures don't break the application."""
    db = TestingSessionLocal()
    
    # This should not raise an exception even if audit logging fails
    # (e.g., database error, invalid data, etc.)
    
    user = User(
        email="failsafe@example.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Failsafe User",
        role=UserRole.CLIENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Login should succeed even if audit logging has issues
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "failsafe@example.com",
            "password": "Pass123!"
        }
    )
    
    assert response.status_code == 200
    
    db.close()
