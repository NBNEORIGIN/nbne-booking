import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

from api.main import app
from api.core.database import Base, get_db
from api.models.tenant import Tenant
from api.models.user import User, UserRole
from api.models.service import Service
from api.models.booking import Booking, BookingStatus
from api.core.security import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tenant_isolation.db"
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
def setup_tenants_and_users():
    """Create two tenants with users and data."""
    db = TestingSessionLocal()
    
    # Create Tenant A
    tenant_a = Tenant(
        slug="tenant-a",
        name="Tenant A",
        email="a@example.com",
        is_active=True
    )
    db.add(tenant_a)
    db.flush()
    
    # Create Tenant B
    tenant_b = Tenant(
        slug="tenant-b",
        name="Tenant B",
        email="b@example.com",
        is_active=True
    )
    db.add(tenant_b)
    db.flush()
    
    # Create Superadmin
    superadmin = User(
        email="superadmin@example.com",
        hashed_password=get_password_hash("SuperPass123!"),
        full_name="Super Admin",
        role=UserRole.SUPERADMIN,
        is_active=True
    )
    db.add(superadmin)
    
    # Create Staff
    staff = User(
        email="staff@example.com",
        hashed_password=get_password_hash("StaffPass123!"),
        full_name="Staff User",
        role=UserRole.STAFF,
        is_active=True
    )
    db.add(staff)
    
    # Create Client for Tenant A
    client_a = User(
        email="client-a@example.com",
        hashed_password=get_password_hash("ClientPass123!"),
        full_name="Client A",
        role=UserRole.CLIENT,
        tenant_id=tenant_a.id,
        is_active=True
    )
    db.add(client_a)
    
    # Create Client for Tenant B
    client_b = User(
        email="client-b@example.com",
        hashed_password=get_password_hash("ClientPass123!"),
        full_name="Client B",
        role=UserRole.CLIENT,
        tenant_id=tenant_b.id,
        is_active=True
    )
    db.add(client_b)
    
    # Create Service for Tenant A
    service_a = Service(
        tenant_id=tenant_a.id,
        name="Service A",
        duration_minutes=30,
        price=50.00,
        is_active=True
    )
    db.add(service_a)
    db.flush()
    
    # Create Service for Tenant B
    service_b = Service(
        tenant_id=tenant_b.id,
        name="Service B",
        duration_minutes=60,
        price=100.00,
        is_active=True
    )
    db.add(service_b)
    db.flush()
    
    # Create Booking for Tenant A
    booking_a = Booking(
        tenant_id=tenant_a.id,
        service_id=service_a.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, minutes=30),
        customer_name="Customer A",
        customer_email="customer-a@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking_a)
    
    # Create Booking for Tenant B
    booking_b = Booking(
        tenant_id=tenant_b.id,
        service_id=service_b.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
        customer_name="Customer B",
        customer_email="customer-b@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking_b)
    
    db.commit()
    
    data = {
        "tenant_a_id": tenant_a.id,
        "tenant_b_id": tenant_b.id,
        "service_a_id": service_a.id,
        "service_b_id": service_b.id,
        "booking_a_id": booking_a.id,
        "booking_b_id": booking_b.id,
        "superadmin_token": create_access_token({"sub": superadmin.id, "email": superadmin.email, "role": "superadmin"}),
        "staff_token": create_access_token({"sub": staff.id, "email": staff.email, "role": "staff"}),
        "client_a_token": create_access_token({"sub": client_a.id, "email": client_a.email, "role": "client"}),
        "client_b_token": create_access_token({"sub": client_b.id, "email": client_b.email, "role": "client"}),
    }
    
    db.close()
    return data


def test_client_cannot_access_other_tenant_bookings(setup_tenants_and_users):
    """Test that Client A cannot access Tenant B's bookings."""
    data = setup_tenants_and_users
    
    # Client A tries to list bookings with Tenant B context
    response = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['client_a_token']}",
            "X-Tenant-Slug": "tenant-b"
        }
    )
    
    # Should be forbidden
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_client_can_access_own_tenant_bookings(setup_tenants_and_users):
    """Test that Client A can access Tenant A's bookings."""
    data = setup_tenants_and_users
    
    response = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['client_a_token']}",
            "X-Tenant-Slug": "tenant-a"
        }
    )
    
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) == 1
    assert bookings[0]["customer_name"] == "Customer A"


def test_staff_can_access_any_tenant(setup_tenants_and_users):
    """Test that staff can access any tenant's data."""
    data = setup_tenants_and_users
    
    # Staff accesses Tenant A
    response_a = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['staff_token']}",
            "X-Tenant-Slug": "tenant-a"
        }
    )
    assert response_a.status_code == 200
    
    # Staff accesses Tenant B
    response_b = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['staff_token']}",
            "X-Tenant-Slug": "tenant-b"
        }
    )
    assert response_b.status_code == 200


def test_superadmin_can_access_any_tenant(setup_tenants_and_users):
    """Test that superadmin can access any tenant's data."""
    data = setup_tenants_and_users
    
    # Superadmin accesses Tenant A
    response_a = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['superadmin_token']}",
            "X-Tenant-Slug": "tenant-a"
        }
    )
    assert response_a.status_code == 200
    
    # Superadmin accesses Tenant B
    response_b = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['superadmin_token']}",
            "X-Tenant-Slug": "tenant-b"
        }
    )
    assert response_b.status_code == 200


def test_client_cannot_access_booking_by_id_from_other_tenant(setup_tenants_and_users):
    """Test that Client A cannot access Tenant B's booking by ID."""
    data = setup_tenants_and_users
    
    # Client A tries to access Tenant B's booking
    response = client.get(
        f"/api/v1/bookings/{data['booking_b_id']}",
        headers={
            "Authorization": f"Bearer {data['client_a_token']}",
            "X-Tenant-Slug": "tenant-a"
        }
    )
    
    # Should return 404 (not 403 to avoid information leakage)
    assert response.status_code == 404


def test_unauthenticated_cannot_access_bookings():
    """Test that unauthenticated requests are rejected."""
    response = client.get(
        "/api/v1/bookings/",
        headers={"X-Tenant-Slug": "tenant-a"}
    )
    
    assert response.status_code == 403


def test_client_cannot_list_all_tenants(setup_tenants_and_users):
    """Test that clients cannot list all tenants."""
    data = setup_tenants_and_users
    
    response = client.get(
        "/api/v1/tenants/",
        headers={"Authorization": f"Bearer {data['client_a_token']}"}
    )
    
    # Clients should not have access
    assert response.status_code == 403


def test_staff_can_list_tenants(setup_tenants_and_users):
    """Test that staff can list tenants."""
    data = setup_tenants_and_users
    
    response = client.get(
        "/api/v1/tenants/",
        headers={"Authorization": f"Bearer {data['staff_token']}"}
    )
    
    assert response.status_code == 200
    tenants = response.json()
    assert len(tenants) >= 2


def test_only_superadmin_can_create_tenant(setup_tenants_and_users):
    """Test that only superadmin can create tenants."""
    data = setup_tenants_and_users
    
    tenant_data = {
        "slug": "new-tenant",
        "name": "New Tenant",
        "email": "new@example.com"
    }
    
    # Client tries
    response_client = client.post(
        "/api/v1/tenants/",
        json=tenant_data,
        headers={"Authorization": f"Bearer {data['client_a_token']}"}
    )
    assert response_client.status_code == 403
    
    # Staff tries
    response_staff = client.post(
        "/api/v1/tenants/",
        json=tenant_data,
        headers={"Authorization": f"Bearer {data['staff_token']}"}
    )
    assert response_staff.status_code == 403
    
    # Superadmin succeeds
    response_superadmin = client.post(
        "/api/v1/tenants/",
        json=tenant_data,
        headers={"Authorization": f"Bearer {data['superadmin_token']}"}
    )
    assert response_superadmin.status_code == 201


def test_only_superadmin_can_delete_tenant(setup_tenants_and_users):
    """Test that only superadmin can delete tenants."""
    data = setup_tenants_and_users
    
    # Staff tries
    response_staff = client.delete(
        f"/api/v1/tenants/{data['tenant_a_id']}",
        headers={"Authorization": f"Bearer {data['staff_token']}"}
    )
    assert response_staff.status_code == 403
    
    # Client tries
    response_client = client.delete(
        f"/api/v1/tenants/{data['tenant_a_id']}",
        headers={"Authorization": f"Bearer {data['client_a_token']}"}
    )
    assert response_client.status_code == 403
    
    # Superadmin succeeds
    response_superadmin = client.delete(
        f"/api/v1/tenants/{data['tenant_a_id']}",
        headers={"Authorization": f"Bearer {data['superadmin_token']}"}
    )
    assert response_superadmin.status_code == 204


def test_tenant_data_completely_isolated(setup_tenants_and_users):
    """Comprehensive test that tenant data is completely isolated."""
    data = setup_tenants_and_users
    
    # Client A lists bookings - should only see Tenant A data
    response = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['client_a_token']}",
            "X-Tenant-Slug": "tenant-a"
        }
    )
    
    assert response.status_code == 200
    bookings = response.json()
    
    # Should only have 1 booking (Tenant A's)
    assert len(bookings) == 1
    assert bookings[0]["customer_name"] == "Customer A"
    assert bookings[0]["customer_email"] == "customer-a@example.com"
    
    # Verify no Tenant B data leaked
    for booking in bookings:
        assert booking["customer_name"] != "Customer B"
        assert booking["customer_email"] != "customer-b@example.com"


def test_cannot_manipulate_tenant_id_in_request(setup_tenants_and_users):
    """Test that users cannot manipulate tenant_id in request body."""
    data = setup_tenants_and_users
    
    # This test would require creating a booking endpoint that accepts tenant_id
    # The key is that tenant_id should ALWAYS come from authentication context
    # not from user input
    
    # For now, verify that tenant context comes from header/subdomain only
    response = client.get(
        "/api/v1/bookings/",
        headers={
            "Authorization": f"Bearer {data['client_a_token']}",
            "X-Tenant-Slug": "tenant-b"  # Client A tries to access Tenant B
        }
    )
    
    # Should be denied
    assert response.status_code == 403
