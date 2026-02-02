import pytest
from fastapi import status
from datetime import time, datetime, timedelta, date


def test_generate_slots_basic(client, test_tenant, db):
    """Test basic slot generation."""
    from api.models.service import Service
    from api.models.availability import Availability
    
    # Create service
    service = Service(
        tenant_id=test_tenant.id,
        name="30-min Service",
        duration_minutes=30,
        is_active=True
    )
    db.add(service)
    
    # Create availability (Monday 9am-5pm)
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
    
    response = client.get(
        f"/api/v1/slots/?service_id={service.id}&start_date={next_monday}&days=1",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["service_id"] == service.id
    assert data["duration_minutes"] == 30
    assert len(data["slots"]) == 16  # 8 hours * 2 slots per hour


def test_generate_slots_with_blackout(client, test_tenant, db):
    """Test that slots are excluded during blackouts."""
    from api.models.service import Service
    from api.models.availability import Availability, Blackout
    
    # Create service
    service = Service(
        tenant_id=test_tenant.id,
        name="60-min Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    # Create availability (Monday 9am-5pm)
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    
    # Find next Monday
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    # Create blackout from 12pm-2pm on that Monday
    blackout = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=datetime.combine(next_monday, time(12, 0)),
        end_datetime=datetime.combine(next_monday, time(14, 0)),
        reason="Lunch break"
    )
    db.add(blackout)
    db.commit()
    db.refresh(service)
    
    response = client.get(
        f"/api/v1/slots/?service_id={service.id}&start_date={next_monday}&days=1",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Should have 8 hours - 2 hours blackout = 6 slots
    assert len(data["slots"]) == 6
    
    # Verify no slots during blackout period
    slot_times = [slot["start_time"] for slot in data["slots"]]
    blackout_start = datetime.combine(next_monday, time(12, 0)).isoformat()
    blackout_end = datetime.combine(next_monday, time(13, 0)).isoformat()
    assert blackout_start not in slot_times
    assert blackout_end not in slot_times


def test_generate_slots_multiple_days(client, test_tenant, db):
    """Test slot generation across multiple days."""
    from api.models.service import Service
    from api.models.availability import Availability
    
    # Create service
    service = Service(
        tenant_id=test_tenant.id,
        name="Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    # Create availability for Monday and Tuesday
    avail_mon = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    avail_tue = Availability(
        tenant_id=test_tenant.id,
        day_of_week=1,
        start_time=time(10, 0),
        end_time=time(16, 0)
    )
    db.add(avail_mon)
    db.add(avail_tue)
    db.commit()
    db.refresh(service)
    
    # Find next Monday
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    response = client.get(
        f"/api/v1/slots/?service_id={service.id}&start_date={next_monday}&days=2",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Monday: 8 slots (9am-5pm), Tuesday: 6 slots (10am-4pm)
    assert len(data["slots"]) == 14


def test_generate_slots_no_availability(client, test_tenant, db):
    """Test that no slots are generated when there's no availability."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Service",
        duration_minutes=30,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    today = date.today()
    
    response = client.get(
        f"/api/v1/slots/?service_id={service.id}&start_date={today}&days=7",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["slots"]) == 0


def test_generate_slots_service_not_found(client, test_tenant):
    """Test that 404 is returned for non-existent service."""
    today = date.today()
    
    response = client.get(
        f"/api/v1/slots/?service_id=99999&start_date={today}&days=7",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_generate_slots_wrong_tenant(client, test_tenant, test_tenant_2, db):
    """Test that slots cannot be generated for another tenant's service."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Service",
        duration_minutes=30,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    today = date.today()
    
    response = client.get(
        f"/api/v1/slots/?service_id={service.id}&start_date={today}&days=7",
        headers={"X-Tenant-Slug": test_tenant_2.slug}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_generate_slots_invalid_date_range(client, test_tenant, db):
    """Test validation of date range."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Service",
        duration_minutes=30,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # end_date before start_date
    response = client.get(
        f"/api/v1/slots/?service_id={service.id}&start_date={today}&end_date={yesterday}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_generate_slots_date_range_too_large(client, test_tenant, db):
    """Test that date range is limited to 90 days."""
    from api.models.service import Service
    
    service = Service(
        tenant_id=test_tenant.id,
        name="Service",
        duration_minutes=30,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    today = date.today()
    far_future = today + timedelta(days=100)
    
    response = client.get(
        f"/api/v1/slots/?service_id={service.id}&start_date={today}&end_date={far_future}",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_generate_slots_varying_durations(client, test_tenant, db):
    """Test slot generation with different service durations."""
    from api.models.service import Service
    from api.models.availability import Availability
    
    # Create availability (Monday 9am-11am, 2 hours)
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(11, 0)
    )
    db.add(availability)
    
    # Find next Monday
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    # Test 30-minute service (should get 4 slots)
    service_30 = Service(
        tenant_id=test_tenant.id,
        name="30-min Service",
        duration_minutes=30,
        is_active=True
    )
    db.add(service_30)
    db.commit()
    db.refresh(service_30)
    
    response = client.get(
        f"/api/v1/slots/?service_id={service_30.id}&start_date={next_monday}&days=1",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["slots"]) == 4
    
    # Test 60-minute service (should get 2 slots)
    service_60 = Service(
        tenant_id=test_tenant.id,
        name="60-min Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service_60)
    db.commit()
    db.refresh(service_60)
    
    response = client.get(
        f"/api/v1/slots/?service_id={service_60.id}&start_date={next_monday}&days=1",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["slots"]) == 2
    
    # Test 90-minute service (should get 1 slot)
    service_90 = Service(
        tenant_id=test_tenant.id,
        name="90-min Service",
        duration_minutes=90,
        is_active=True
    )
    db.add(service_90)
    db.commit()
    db.refresh(service_90)
    
    response = client.get(
        f"/api/v1/slots/?service_id={service_90.id}&start_date={next_monday}&days=1",
        headers={"X-Tenant-Slug": test_tenant.slug}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["slots"]) == 1


def test_slot_generator_is_slot_available(test_tenant, db):
    """Test the is_slot_available method for booking validation."""
    from api.models.service import Service
    from api.models.availability import Availability, Blackout
    from api.services.slot_generator import SlotGenerator
    
    # Create service
    service = Service(
        tenant_id=test_tenant.id,
        name="Service",
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    
    # Create availability (Monday 9am-5pm)
    availability = Availability(
        tenant_id=test_tenant.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    db.add(availability)
    
    # Find next Monday
    today = date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    
    db.commit()
    db.refresh(service)
    
    generator = SlotGenerator(db, test_tenant.id)
    
    # Test valid slot
    slot_start = datetime.combine(next_monday, time(10, 0))
    slot_end = datetime.combine(next_monday, time(11, 0))
    assert generator.is_slot_available(service.id, slot_start, slot_end) is True
    
    # Test slot outside availability
    slot_start = datetime.combine(next_monday, time(18, 0))
    slot_end = datetime.combine(next_monday, time(19, 0))
    assert generator.is_slot_available(service.id, slot_start, slot_end) is False
    
    # Add blackout and test
    blackout = Blackout(
        tenant_id=test_tenant.id,
        start_datetime=datetime.combine(next_monday, time(14, 0)),
        end_datetime=datetime.combine(next_monday, time(15, 0))
    )
    db.add(blackout)
    db.commit()
    
    slot_start = datetime.combine(next_monday, time(14, 0))
    slot_end = datetime.combine(next_monday, time(15, 0))
    assert generator.is_slot_available(service.id, slot_start, slot_end) is False
