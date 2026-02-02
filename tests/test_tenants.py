import pytest
from fastapi import status


def test_create_tenant(client):
    """Test creating a new tenant."""
    response = client.post(
        "/api/v1/tenants/",
        json={
            "slug": "new-tenant",
            "name": "New Tenant",
            "subdomain": "new",
            "email": "new@example.com",
            "phone": "+1-555-1234",
            "is_active": True,
            "settings": {}
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["slug"] == "new-tenant"
    assert data["name"] == "New Tenant"
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "created_at" in data


def test_create_tenant_duplicate_slug(client, test_tenant):
    """Test that creating a tenant with duplicate slug fails."""
    response = client.post(
        "/api/v1/tenants/",
        json={
            "slug": test_tenant.slug,
            "name": "Duplicate Tenant",
            "email": "duplicate@example.com",
            "is_active": True,
            "settings": {}
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_create_tenant_duplicate_subdomain(client, test_tenant):
    """Test that creating a tenant with duplicate subdomain fails."""
    response = client.post(
        "/api/v1/tenants/",
        json={
            "slug": "different-slug",
            "name": "Different Tenant",
            "subdomain": test_tenant.subdomain,
            "email": "different@example.com",
            "is_active": True,
            "settings": {}
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_list_tenants(client, test_tenant, test_tenant_2):
    """Test listing all tenants."""
    response = client.get("/api/v1/tenants/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    slugs = [t["slug"] for t in data]
    assert test_tenant.slug in slugs
    assert test_tenant_2.slug in slugs


def test_get_tenant_by_id(client, test_tenant):
    """Test getting a tenant by ID."""
    response = client.get(f"/api/v1/tenants/{test_tenant.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_tenant.id
    assert data["slug"] == test_tenant.slug


def test_get_tenant_by_slug(client, test_tenant):
    """Test getting a tenant by slug."""
    response = client.get(f"/api/v1/tenants/slug/{test_tenant.slug}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["slug"] == test_tenant.slug
    assert data["name"] == test_tenant.name


def test_get_nonexistent_tenant(client):
    """Test getting a tenant that doesn't exist."""
    response = client.get("/api/v1/tenants/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_tenant(client, test_tenant):
    """Test updating a tenant."""
    response = client.patch(
        f"/api/v1/tenants/{test_tenant.id}",
        json={
            "name": "Updated Name",
            "phone": "+1-555-9999"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["phone"] == "+1-555-9999"
    assert data["slug"] == test_tenant.slug


def test_delete_tenant(client, test_tenant):
    """Test deleting (soft delete) a tenant."""
    response = client.delete(f"/api/v1/tenants/{test_tenant.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify tenant is marked inactive
    response = client.get(f"/api/v1/tenants/{test_tenant.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False


def test_tenant_resolution_by_subdomain(client, test_tenant):
    """Test that tenant is resolved from subdomain in Host header."""
    response = client.get(
        "/health",
        headers={"Host": f"{test_tenant.subdomain}.nbnebookings.co.uk"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_tenant_resolution_by_header(client, test_tenant):
    """Test that tenant is resolved from X-Tenant-Slug header."""
    response = client.get(
        "/health",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK


def test_tenant_slug_validation(client):
    """Test that tenant slug validation works."""
    # Invalid slug with uppercase
    response = client.post(
        "/api/v1/tenants/",
        json={
            "slug": "Invalid-Slug",
            "name": "Invalid Tenant",
            "email": "invalid@example.com",
            "is_active": True,
            "settings": {}
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid slug with spaces
    response = client.post(
        "/api/v1/tenants/",
        json={
            "slug": "invalid slug",
            "name": "Invalid Tenant",
            "email": "invalid@example.com",
            "is_active": True,
            "settings": {}
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
