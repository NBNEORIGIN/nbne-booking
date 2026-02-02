import pytest
from datetime import datetime, timedelta, time, date


def test_admin_bookings_view_loads(client, test_tenant):
    """Test that admin bookings view loads successfully."""
    response = client.get(
        "/admin/bookings",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == 200
    assert b"Bookings" in response.content
    assert b"Export CSV" in response.content


def test_admin_bookings_with_data(client, test_tenant, db):
    """Test admin bookings view displays booking data."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
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
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    db.commit()
    db.refresh(service)
    
    # Create booking
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    start = datetime.combine(next_monday, time(10, 0))
    end = datetime.combine(next_monday, time(11, 0))
    
    booking = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start,
        end_time=end,
        customer_name="John Doe",
        customer_email="john@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(booking)
    db.commit()
    
    # Check view
    response = client.get(
        "/admin/bookings",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == 200
    assert b"John Doe" in response.content
    assert b"Test Service" in response.content


def test_admin_bookings_filter_by_status(client, test_tenant, db):
    """Test filtering bookings by status."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
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
    
    # Create confirmed and cancelled bookings
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    start1 = datetime.combine(next_monday, time(10, 0))
    booking1 = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start1,
        end_time=start1 + timedelta(hours=1),
        customer_name="Confirmed Customer",
        customer_email="confirmed@example.com",
        status=BookingStatus.CONFIRMED
    )
    
    start2 = datetime.combine(next_monday, time(14, 0))
    booking2 = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start2,
        end_time=start2 + timedelta(hours=1),
        customer_name="Cancelled Customer",
        customer_email="cancelled@example.com",
        status=BookingStatus.CANCELLED
    )
    
    db.add_all([booking1, booking2])
    db.commit()
    
    # Filter by confirmed (no status filter for now, just verify both show up)
    response = client.get(
        "/admin/bookings",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == 200
    assert b"Confirmed Customer" in response.content
    assert b"Cancelled Customer" in response.content


def test_csv_export(client, test_tenant, db):
    """Test CSV export functionality."""
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
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
    
    # Create booking
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    start = datetime.combine(next_monday, time(10, 0))
    booking = Booking(
        tenant_id=test_tenant.id,
        service_id=service.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="CSV Test",
        customer_email="csv@example.com",
        customer_phone="+1-555-1234",
        status=BookingStatus.CONFIRMED,
        notes="Test notes"
    )
    db.add(booking)
    db.commit()
    
    # Export CSV
    response = client.get(
        "/admin/bookings/export",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    
    # Check CSV content
    csv_content = response.content.decode('utf-8')
    assert "CSV Test" in csv_content
    assert "csv@example.com" in csv_content
    assert "Test Service" in csv_content
    assert "CONFIRMED" in csv_content.upper()


def test_admin_services_view(client, test_tenant, db):
    """Test admin services view."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Admin Test Service",
        duration_minutes=45,
        is_active=True
    )
    db.add(service)
    db.commit()
    
    response = client.get(
        "/admin/services",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == 200
    assert b"Services" in response.content
    assert b"Admin Test Service" in response.content
    assert b"45 minutes" in response.content


def test_admin_availability_view(client, test_tenant, db):
    """Test admin availability view."""
    from api.models.availability import Availability
    
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    db.commit()
    
    response = client.get(
        "/admin/availability",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == 200
    assert b"Weekly Availability" in response.content
    assert b"Monday" in response.content


def test_tenant_isolation_admin(client, test_tenant, db):
    """Test that admin views respect tenant isolation."""
    from api.models.tenant import Tenant
    from api.models.service import Service
    from api.models.booking import Booking, BookingStatus
    from api.models.availability import Availability
    
    # Create another tenant
    other_tenant = Tenant(
        name="Other Tenant",
        slug="other-tenant",
        subdomain="other",
        email="other@example.com",
        is_active=True
    )
    db.add(other_tenant)
    db.commit()
    db.refresh(other_tenant)
    
    # Create service for other tenant
    other_service = Service(
        tenant_id=other_tenant.id,
        name="Other Service",
        duration_minutes=30,
        is_active=True
    )
    db.add(other_service)
    
    availability = Availability(
        tenant_id=other_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    db.commit()
    db.refresh(other_service)
    
    # Create booking for other tenant
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    start = datetime.combine(next_monday, time(10, 0))
    other_booking = Booking(
        tenant_id=other_tenant.id,
        service_id=other_service.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        customer_name="Other Customer",
        customer_email="other@example.com",
        status=BookingStatus.CONFIRMED
    )
    db.add(other_booking)
    db.commit()
    
    # Request with test_tenant should not see other tenant's data
    response = client.get(
        "/admin/bookings",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == 200
    assert b"Other Customer" not in response.content
    assert b"Other Service" not in response.content
