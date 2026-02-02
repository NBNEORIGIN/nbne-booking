import pytest
from fastapi import status


def test_create_service(client, test_tenant):
    """Test creating a new service."""
    response = client.post(
        "/api/v1/services/",
        json={
            "name": "Haircut",
            "description": "Standard haircut service",
            "duration_minutes": 30,
            "price": 25.00,
            "is_active": True
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Haircut"
    assert data["duration_minutes"] == 30
    assert data["price"] == 25.00
    assert data["tenant_id"] == test_tenant.id
    assert "id" in data


def test_create_service_without_tenant(client):
    """Test that creating a service without tenant context fails."""
    response = client.post(
        "/api/v1/services/",
        json={
            "name": "Haircut",
            "duration_minutes": 30,
            "price": 25.00,
            "is_active": True
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_services(client, test_tenant, db):
    """Test listing services for a tenant."""
    from api.models.service import Service
    
    # Create test services
    service1 = Service(
        tenant_id=test_tenant.id,
        name="Service 1",
        duration_minutes=30,
        price=25.00,
        is_active=True
    )
    service2 = Service(
        tenant_id=test_tenant.id,
        name="Service 2",
        duration_minutes=60,
        price=50.00,
        is_active=True
    )
    db.add(service1)
    db.add(service2)
    db.commit()
    
    response = client.get(
        "/api/v1/services/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    names = [s["name"] for s in data]
    assert "Service 1" in names
    assert "Service 2" in names


def test_list_services_excludes_inactive_by_default(client, test_tenant, db):
    """Test that inactive services are excluded by default."""
    from api.models.service import Service
    
    service_active = Service(
        tenant_id=test_tenant.id,
        name="Active Service",
        duration_minutes=30,
        is_active=True
    )
    service_inactive = Service(
        tenant_id=test_tenant.id,
        name="Inactive Service",
        duration_minutes=30,
        is_active=False
    )
    db.add(service_active)
    db.add(service_inactive)
    db.commit()
    
    response = client.get(
        "/api/v1/services/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Active Service"


def test_list_services_include_inactive(client, test_tenant, db):
    """Test that inactive services can be included with parameter."""
    from api.models.service import Service
    
    service_active = Service(
        tenant_id=test_tenant.id,
        name="Active Service",
        duration_minutes=30,
        is_active=True
    )
    service_inactive = Service(
        tenant_id=test_tenant.id,
        name="Inactive Service",
        duration_minutes=30,
        is_active=False
    )
    db.add(service_active)
    db.add(service_inactive)
    db.commit()
    
    response = client.get(
        "/api/v1/services/?include_inactive=true",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_get_service(client, test_tenant, db):
    """Test getting a specific service."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=45,
        price=35.00
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    response = client.get(
        f"/api/v1/services/{service.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == service.id
    assert data["name"] == "Test Service"


def test_get_service_wrong_tenant(client, test_tenant, test_tenant_2, db):
    """Test that a service cannot be accessed by a different tenant."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Tenant 1 Service",
        duration_minutes=30
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    # Try to access with tenant 2's context
    response = client.get(
        f"/api/v1/services/{service.id}",
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_service(client, test_tenant, db):
    """Test updating a service."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Original Name",
        duration_minutes=30,
        price=25.00
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    response = client.patch(
        f"/api/v1/services/{service.id}",
        json={
            "name": "Updated Name",
            "price": 30.00
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 30.00
    assert data["duration_minutes"] == 30


def test_update_service_wrong_tenant(client, test_tenant, test_tenant_2, db):
    """Test that a service cannot be updated by a different tenant."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Tenant 1 Service",
        duration_minutes=30
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    response = client.patch(
        f"/api/v1/services/{service.id}",
        json={"name": "Hacked Name"},
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_service(client, test_tenant, db):
    """Test deleting (soft delete) a service."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="To Delete",
        duration_minutes=30
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    response = client.delete(
        f"/api/v1/services/{service.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify service is marked inactive
    db.refresh(service)
    assert service.is_active is False


def test_delete_service_wrong_tenant(client, test_tenant, test_tenant_2, db):
    """Test that a service cannot be deleted by a different tenant."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Tenant 1 Service",
        duration_minutes=30
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    response = client.delete(
        f"/api/v1/services/{service.id}",
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Verify service is still active
    db.refresh(service)
    assert service.is_active is True


def test_service_validation(client, test_tenant):
    """Test service input validation."""
    # Invalid duration (0)
    response = client.post(
        "/api/v1/services/",
        json={
            "name": "Invalid Service",
            "duration_minutes": 0,
            "is_active": True
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid duration (negative)
    response = client.post(
        "/api/v1/services/",
        json={
            "name": "Invalid Service",
            "duration_minutes": -10,
            "is_active": True
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid price (negative)
    response = client.post(
        "/api/v1/services/",
        json={
            "name": "Invalid Service",
            "duration_minutes": 30,
            "price": -5.00,
            "is_active": True
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_tenant_isolation_list_services(client, test_tenant, test_tenant_2, db):
    """Test that tenants can only see their own services."""
    from api.models.service import Service
    
    # Create services for both tenants
    service1 = Service(
        tenant_id=test_tenant.id,
        name="Tenant 1 Service",
        duration_minutes=30
    )
    service2 = Service(
        tenant_id=test_tenant_2.id,
        name="Tenant 2 Service",
        duration_minutes=45
    )
    db.add(service1)
    db.add(service2)
    db.commit()
    
    # Tenant 1 should only see their service
    response = client.get(
        "/api/v1/services/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Tenant 1 Service"
    
    # Tenant 2 should only see their service
    response = client.get(
        "/api/v1/services/",
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Tenant 2 Service"
