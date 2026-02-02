import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from api.services.email_service import EmailService


def test_email_service_initialization():
    """Test that EmailService initializes correctly."""
    service = EmailService()
    assert service.smtp_host is not None
    assert service.from_name == "NBNE Booking"


@patch('api.services.email_service.smtplib.SMTP')
def test_send_booking_confirmation_to_customer(mock_smtp):
    """Test sending booking confirmation email to customer."""
    # Mock SMTP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    service = EmailService()
    
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    result = service.send_booking_confirmation_to_customer(
        customer_email="customer@example.com",
        customer_name="John Doe",
        service_name="Consultation",
        start_time=start_time,
        end_time=end_time,
        tenant_name="Acme Corp",
        tenant_email="contact@acme.com",
        tenant_phone="+1-555-1234",
        notes="Please arrive 5 minutes early"
    )
    
    assert result is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()


@patch('api.services.email_service.smtplib.SMTP')
def test_send_booking_notification_to_business(mock_smtp):
    """Test sending booking notification email to business."""
    # Mock SMTP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    service = EmailService()
    
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    result = service.send_booking_notification_to_business(
        business_email="business@example.com",
        business_name="Acme Corp",
        customer_name="John Doe",
        customer_email="customer@example.com",
        customer_phone="+1-555-5678",
        service_name="Consultation",
        start_time=start_time,
        end_time=end_time,
        notes="Customer requested window seat"
    )
    
    assert result is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()


@patch('api.services.email_service.smtplib.SMTP')
def test_email_send_failure_handling(mock_smtp):
    """Test that email send failures are handled gracefully."""
    # Mock SMTP to raise an exception
    mock_smtp.return_value.__enter__.side_effect = Exception("SMTP connection failed")
    
    service = EmailService()
    
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    # Should return False but not raise exception
    result = service.send_booking_confirmation_to_customer(
        customer_email="customer@example.com",
        customer_name="John Doe",
        service_name="Consultation",
        start_time=start_time,
        end_time=end_time,
        tenant_name="Acme Corp",
        tenant_email="contact@acme.com"
    )
    
    assert result is False


def test_booking_creates_with_email_disabled(client, test_tenant, db):
    """Test that bookings work even when email is disabled."""
    from api.models.service import Service
    from api.models.availability import Availability
    from datetime import time, date
    from api.core.config import settings
    
    # Temporarily disable email
    original_setting = settings.ENABLE_EMAIL_NOTIFICATIONS
    settings.ENABLE_EMAIL_NOTIFICATIONS = False
    
    try:
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
                "customer_email": "john@example.com"
            },
            headers={"X-Tenant-Slug": test_tenant.slug}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "John Doe"
    finally:
        # Restore original setting
        settings.ENABLE_EMAIL_NOTIFICATIONS = original_setting


@patch('api.services.email_service.email_service.send_booking_confirmation_to_customer')
@patch('api.services.email_service.email_service.send_booking_notification_to_business')
def test_booking_sends_emails_when_enabled(mock_business_email, mock_customer_email, client, test_tenant, db):
    """Test that bookings trigger email notifications when enabled."""
    from api.models.service import Service
    from api.models.availability import Availability
    from datetime import time, date
    from api.core.config import settings
    
    # Ensure email is enabled
    original_setting = settings.ENABLE_EMAIL_NOTIFICATIONS
    settings.ENABLE_EMAIL_NOTIFICATIONS = True
    
    # Mock email sending to return True
    mock_customer_email.return_value = True
    mock_business_email.return_value = True
    
    try:
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
                "customer_email": "john@example.com"
            },
            headers={"X-Tenant-Slug": test_tenant.slug}
        )
        
        assert response.status_code == 201
        
        # Verify emails were called
        mock_customer_email.assert_called_once()
        mock_business_email.assert_called_once()
        
        # Verify correct parameters
        customer_call = mock_customer_email.call_args
        assert customer_call.kwargs['customer_email'] == "john@example.com"
        assert customer_call.kwargs['customer_name'] == "John Doe"
        assert customer_call.kwargs['service_name'] == "Test Service"
        
    finally:
        # Restore original setting
        settings.ENABLE_EMAIL_NOTIFICATIONS = original_setting
