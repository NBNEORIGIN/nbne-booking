import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

from api.main import app
from api.core.database import Base, get_db
from api.models.user import User, UserRole
from api.core.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
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


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "role": "client"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "hashed_password" not in data


def test_register_duplicate_email():
    """Test that duplicate email registration fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "role": "client"
    }
    
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201
    
    response2 = client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"]


def test_register_weak_password():
    """Test that weak passwords are rejected."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "password": "weak",
            "full_name": "Test User",
            "role": "client"
        }
    )
    assert response.status_code == 422


def test_login_success():
    """Test successful login."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "SecurePass123!",
            "full_name": "Login User",
            "role": "client"
        }
    )
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "role": "client"
        }
    )
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401


def test_login_nonexistent_user():
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 401


def test_account_lockout():
    """Test account lockout after failed login attempts."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "lockout@example.com",
            "password": "SecurePass123!",
            "full_name": "Lockout User",
            "role": "client"
        }
    )
    
    for _ in range(5):
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "lockout@example.com",
                "password": "WrongPassword!"
            }
        )
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "lockout@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 403
    assert "locked" in response.json()["detail"].lower()


def test_get_current_user():
    """Test getting current user info."""
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "current@example.com",
            "password": "SecurePass123!",
            "full_name": "Current User",
            "role": "client"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "current@example.com",
            "password": "SecurePass123!"
        }
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["full_name"] == "Current User"


def test_unauthorized_access():
    """Test that endpoints require authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_password_change():
    """Test password change."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "change@example.com",
            "password": "OldPass123!",
            "full_name": "Change User",
            "role": "client"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "change@example.com",
            "password": "OldPass123!"
        }
    )
    token = login_response.json()["access_token"]
    
    change_response = client.post(
        "/api/v1/auth/password-change",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "OldPass123!",
            "new_password": "NewPass456!"
        }
    )
    assert change_response.status_code == 200
    
    new_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "change@example.com",
            "password": "NewPass456!"
        }
    )
    assert new_login.status_code == 200
