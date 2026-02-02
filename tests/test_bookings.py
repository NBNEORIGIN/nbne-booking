import pytest
from fastapi import status
from datetime import time, datetime, timedelta, date
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def test_create_booking(client, test_tenant, db):
    """Test creating a new booking."""
    from api.models.service import Service
    from api.models.availability import Availability
    
    # Create service and availability
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,  # Monday
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    db.commit()
    db.refresh(service)
    
    # Find next Monday
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    start = datetime.combine(next_monday, time(10, 0))
    end = datetime.combine(next_monday, time(11, 0))
    
    response = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+1-555-1234"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["customer_name"] == "John Doe"
    assert data["customer_email"] == "john@example.com"
    assert data["status"] == "confirmed"


def test_create_booking_invalid_times(client, test_tenant, db):
    """Test that end_time must be after start_time."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    start = datetime.now() + timedelta(days=1)
    end = start - timedelta(hours=1)
    
    response = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_booking_outside_availability(client, test_tenant, db):
    """Test that bookings cannot be created outside availability windows."""
    from api.models.service import Service
    from api.models.availability import Availability
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    # Availability only 9am-5pm
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    db.commit()
    db.refresh(service)
    
    # Try to book at 8pm (outside availability)
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    start = datetime.combine(next_monday, time(20, 0))
    end = datetime.combine(next_monday, time(21, 0))
    
    response = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not available" in response.json()["detail"].lower()


def test_create_booking_during_blackout(client, test_tenant, db):
    """Test that bookings cannot be created during blackouts."""
    from api.models.service import Service
    from api.models.availability import Availability, Blackout
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    # Blackout from 12pm-2pm
    blackout = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=datetime.combine(next_monday, time(12, 0)),
        end_datetime=datetime.combine(next_monday, time(14, 0))
    )
    db.add(blackout)
    db.commit()
    db.refresh(service)
    
    # Try to book at 1pm (during blackout)
    start = datetime.combine(next_monday, time(13, 0))
    end = datetime.combine(next_monday, time(14, 0))
    
    response = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_double_booking_prevention(client, test_tenant, db):
    """Test that double bookings are prevented."""
    from api.models.service import Service
    from api.models.availability import Availability
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    db.commit()
    db.refresh(service)
    
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    start = datetime.combine(next_monday, time(10, 0))
    end = datetime.combine(next_monday, time(11, 0))
    
    # First booking should succeed
    response1 = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "customer_name": "Customer 1",
            "customer_email": "customer1@example.com"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Second booking at same time should fail
    response2 = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "customer_name": "Customer 2",
            "customer_email": "customer2@example.com"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert "already booked" in response2.json()["detail"].lower()


def test_overlapping_booking_prevention(client, test_tenant, db):
    """Test that overlapping bookings are prevented."""
    from api.models.service import Service
    from api.models.availability import Availability
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    db.commit()
    db.refresh(service)
    
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    # First booking 10am-11am
    start1 = datetime.combine(next_monday, time(10, 0))
    end1 = datetime.combine(next_monday, time(11, 0))
    
    response1 = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start1.isoformat(),
            "end_time": end1.isoformat(),
            "customer_name": "Customer 1",
            "customer_email": "customer1@example.com"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Try to book 10:30am-11:30am (overlaps)
    start2 = datetime.combine(next_monday, time(10, 30))
    end2 = datetime.combine(next_monday, time(11, 30))
    
    response2 = client.post(
        "/api/v1/bookings/",
        json={
            "service_id": service.id,
            "start_time": start2.isoformat(),
            "end_time": end2.isoformat(),
            "customer_name": "Customer 2",
            "customer_email": "customer2@example.com"
        },
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response2.status_code == status.HTTP_409_CONFLICT


def test_list_bookings(client, test_tenant, db):
    """Test listing bookings."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    # Create test bookings
    start = datetime.now() + timedelta(days=1)
    booking1 = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="Customer 1",
        customer_email="customer1@example.com",
        status=BookingStatus.CONFIRMED
    )
    booking2 = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start + timedelta(days=1),
        end_time=start + timedelta(days=1, hours=1),
        customer_name="Customer 2",
        customer_email="customer2@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking1)
    db.add(booking2)
    db.commit()
    
    response = client.get(
        "/api/v1/bookings/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_get_booking(client, test_tenant, db):
    """Test getting a specific booking."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    start = datetime.now() + timedelta(days=1)
    booking = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="John Doe",
        customer_email="john@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    response = client.get(
        f"/api/v1/bookings/{booking.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == booking.id
    assert data["customer_name"] == "John Doe"


def test_get_booking_wrong_tenant(client, test_tenant, test_tenant_2, db):
    """Test that bookings cannot be accessed by different tenant."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    start = datetime.now() + timedelta(days=1)
    booking = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="John Doe",
        customer_email="john@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    response = client.get(
        f"/api/v1/bookings/{booking.id}",
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_booking(client, test_tenant, db):
    """Test updating a booking."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    start = datetime.now() + timedelta(days=1)
    booking = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="John Doe",
        customer_email="john@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    response = client.patch(
        f"/api/v1/bookings/{booking.id}",
        json={"notes": "Customer requested window seat"},
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["notes"] == "Customer requested window seat"


def test_cancel_booking(client, test_tenant, db):
    """Test cancelling a booking."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Test Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    start = datetime.now() + timedelta(days=1)
    booking = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="John Doe",
        customer_email="john@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    response = client.delete(
        f"/api/v1/bookings/{booking.id}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify status changed to cancelled
    db.refresh(booking)
    assert booking.status == BookingStatus.CANCELLED


def test_tenant_isolation_bookings(client, test_tenant, test_tenant_2, db):
    """Test that tenants can only see their own bookings."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
    
    service1 = Service(
        tenant_id=test_tenant.id,
        name="Service 1",
        duration_minutes=60,
        is_active=True
    )
    service2 = Service(
        tenant_id=test_tenant_2.id,
        name="Service 2",
        duration_minutes=60,
        is_active=True
    )
    db.add(service1)
    db.add(service2)
    db.commit()
    
    start = datetime.now() + timedelta(days=1)
    booking1 = Booking(
        tenant_id=test_tenant.id,
        service_id=service1.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="Tenant 1 Customer",
        customer_email="customer1@example.com",
        status=BookingStatus.CONFIRMED
    )
    booking2 = Booking(
        tenant_id=test_tenant_2.id,
        service_id=service2.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="Tenant 2 Customer",
        customer_email="customer2@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking1)
    db.add(booking2)
    db.commit()
    
    # Tenant 1 should only see their booking
    response = client.get(
        "/api/v1/bookings/",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_name"] == "Tenant 1 Customer"
