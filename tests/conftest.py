import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from api.core.database import Base, get_db
from api.models.tenant import Tenant

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_tenant(db):
    tenant = Tenant(
        slug="test-tenant",
        name="Test Tenant",
        subdomain="test",
        email="test@example.com",
        phone="+1-555-0000",
        is_active=True,
        settings={"timezone": "UTC"}
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture
def test_tenant_2(db):
    tenant = Tenant(
        slug="test-tenant-2",
        name="Test Tenant 2",
        subdomain="test2",
        email="test2@example.com",
        phone="+1-555-0001",
        is_active=True,
        settings={"timezone": "UTC"}
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant
