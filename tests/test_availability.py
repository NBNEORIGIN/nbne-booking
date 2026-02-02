import pytest
from fastapi import status
from datetime import time, datetime, timedelta


def test_create_availability(client, test_tenant):
    """Test creating a new availability window."""
    response = client.post(
        "/api/v1/availability/",
        json={
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "17:00:00"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["day_of_week"] == 1
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "17:00:00"
    assert data["tenant_id"] == test_tenant.id


def test_create_availability_invalid_times(client, test_tenant):
    """Test that end_time must be after start_time."""
    response = client.post(
        "/api/v1/availability/",
        json={
            "day_of_week": 1,
            "start_time": "17:00:00",
            "end_time": "09:00:00"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_availability(client, test_tenant, db):
    """Test listing availability windows."""
    from api.models.availability import Availability
    
    avail1 = Availability(
        tenant_id=test_tenant.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    avail2 = Availability(
        tenant_id=test_tenant.id,
        day_of_week=2,
        start_time=time(10, 0),
        end_time=time(18, 0)
    )
    db.add(avail1)
    db.add(avail2)
    db.commit()
    
    response = client.get(
        "/api/v1/availability/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_get_availability(client, test_tenant, db):
    """Test getting a specific availability window."""
    from api.models.availability import Availability
    
    avail = Availability(
        tenant_id=test_tenant.id,
        day_of_week=3,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(avail)
    db.commit()
    db.refresh(avail)
    
    response = client.get(
        f"/api/v1/availability/{avail.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == avail.id
    assert data["day_of_week"] == 3


def test_get_availability_wrong_tenant(client, test_tenant, test_tenant_2, db):
    """Test that availability cannot be accessed by a different tenant."""
    from api.models.availability import Availability
    
    avail = Availability(
        tenant_id=test_tenant.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(avail)
    db.commit()
    db.refresh(avail)
    
    response = client.get(
        f"/api/v1/availability/{avail.id}",
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_availability(client, test_tenant, db):
    """Test updating an availability window."""
    from api.models.availability import Availability
    
    avail = Availability(
        tenant_id=test_tenant.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(avail)
    db.commit()
    db.refresh(avail)
    
    response = client.patch(
        f"/api/v1/availability/{avail.id}",
        json={"end_time": "18:00:00"},
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["end_time"] == "18:00:00"
    assert data["start_time"] == "09:00:00"


def test_delete_availability(client, test_tenant, db):
    """Test deleting an availability window."""
    from api.models.availability import Availability
    
    avail = Availability(
        tenant_id=test_tenant.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(avail)
    db.commit()
    db.refresh(avail)
    
    response = client.delete(
        f"/api/v1/availability/{avail.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    response = client.get(
        f"/api/v1/availability/{avail.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_blackout(client, test_tenant):
    """Test creating a new blackout."""
    start = datetime.now() + timedelta(days=1)
    end = start + timedelta(hours=2)
    
    response = client.post(
        "/api/v1/blackouts/",
        json={
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
            "reason": "Holiday"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["reason"] == "Holiday"
    assert data["tenant_id"] == test_tenant.id


def test_create_blackout_invalid_times(client, test_tenant):
    """Test that end_datetime must be after start_datetime."""
    start = datetime.now() + timedelta(days=1)
    end = start - timedelta(hours=2)
    
    response = client.post(
        "/api/v1/blackouts/",
        json={
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
            "reason": "Invalid"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_blackouts(client, test_tenant, db):
    """Test listing blackouts."""
    from api.models.availability import Blackout
    
    start1 = datetime.now() + timedelta(days=1)
    blackout1 = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=start1,
        end_datetime=start1 + timedelta(hours=2),
        reason="Blackout 1"
    )
    start2 = datetime.now() + timedelta(days=2)
    blackout2 = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=start2,
        end_datetime=start2 + timedelta(hours=3),
        reason="Blackout 2"
    )
    db.add(blackout1)
    db.add(blackout2)
    db.commit()
    
    response = client.get(
        "/api/v1/blackouts/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_list_blackouts_with_date_filter(client, test_tenant, db):
    """Test listing blackouts with date filters."""
    from api.models.availability import Blackout
    
    base = datetime.now()
    blackout1 = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=base + timedelta(days=1),
        end_datetime=base + timedelta(days=1, hours=2)
    )
    blackout2 = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=base + timedelta(days=10),
        end_datetime=base + timedelta(days=10, hours=2)
    )
    db.add(blackout1)
    db.add(blackout2)
    db.commit()
    
    # Filter to only get blackouts in next 5 days
    end_filter = base + timedelta(days=5)
    response = client.get(
        f"/api/v1/blackouts/?end_date={end_filter.isoformat()}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1


def test_get_blackout(client, test_tenant, db):
    """Test getting a specific blackout."""
    from api.models.availability import Blackout
    
    start = datetime.now() + timedelta(days=1)
    blackout = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2),
        reason="Test Blackout"
    )
    db.add(blackout)
    db.commit()
    db.refresh(blackout)
    
    response = client.get(
        f"/api/v1/blackouts/{blackout.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == blackout.id
    assert data["reason"] == "Test Blackout"


def test_get_blackout_wrong_tenant(client, test_tenant, test_tenant_2, db):
    """Test that blackout cannot be accessed by a different tenant."""
    from api.models.availability import Blackout
    
    start = datetime.now() + timedelta(days=1)
    blackout = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2)
    )
    db.add(blackout)
    db.commit()
    db.refresh(blackout)
    
    response = client.get(
        f"/api/v1/blackouts/{blackout.id}",
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_blackout(client, test_tenant, db):
    """Test updating a blackout."""
    from api.models.availability import Blackout
    
    start = datetime.now() + timedelta(days=1)
    blackout = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2),
        reason="Original"
    )
    db.add(blackout)
    db.commit()
    db.refresh(blackout)
    
    response = client.patch(
        f"/api/v1/blackouts/{blackout.id}",
        json={"reason": "Updated Reason"},
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["reason"] == "Updated Reason"


def test_delete_blackout(client, test_tenant, db):
    """Test deleting a blackout."""
    from api.models.availability import Blackout
    
    start = datetime.now() + timedelta(days=1)
    blackout = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2)
    )
    db.add(blackout)
    db.commit()
    db.refresh(blackout)
    
    response = client.delete(
        f"/api/v1/blackouts/{blackout.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    response = client.get(
        f"/api/v1/blackouts/{blackout.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_tenant_isolation_availability(client, test_tenant, test_tenant_2, db):
    """Test that tenants can only see their own availability."""
    from api.models.availability import Availability
    
    avail1 = Availability(
        tenant_id=test_tenant.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    avail2 = Availability(
        tenant_id=test_tenant_2.id,
        day_of_week=1,
        start_time=time(10, 0),
        end_time=time(18, 0)
    )
    db.add(avail1)
    db.add(avail2)
    db.commit()
    
    # Tenant 1 should only see their availability
    response = client.get(
        "/api/v1/availability/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["tenant_id"] == test_tenant.id


def test_tenant_isolation_blackouts(client, test_tenant, test_tenant_2, db):
    """Test that tenants can only see their own blackouts."""
    from api.models.availability import Blackout
    
    start = datetime.now() + timedelta(days=1)
    blackout1 = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2)
    )
    blackout2 = Blackout(
        tenant_id=test_tenant_2.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2)
    )
    db.add(blackout1)
    db.add(blackout2)
    db.commit()
    
    # Tenant 1 should only see their blackout
    response = client.get(
        "/api/v1/blackouts/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["tenant_id"] == test_tenant.id
