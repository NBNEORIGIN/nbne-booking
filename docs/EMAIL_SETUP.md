# Email Notification Setup

## Overview
The NBNE Booking system sends automated email notifications for booking confirmations. This document explains how to configure email notifications.

## Email Types

### 1. Customer Confirmation Email
Sent to the customer when a booking is created.

**Contains:**
- Booking confirmation message
- Service name and details
- Date, time, and duration
- Business contact information
- Any special notes

### 2. Business Notification Email
Sent to the business when a new booking is received.

**Contains:**
- New booking alert
- Customer information (name, email, phone)
- Service details
- Date, time, and duration
- Customer notes

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=NBNE Booking

# Feature Flags
ENABLE_EMAIL_NOTIFICATIONS=true
```

### Gmail Setup

If using Gmail:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password:**
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and your device
   - Copy the generated 16-character password
3. **Use the App Password** as `SMTP_PASSWORD` (not your regular Gmail password)

### Other SMTP Providers

**SendGrid:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

**Amazon SES:**
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

## Testing Email Notifications

### 1. Disable Emails for Development
```bash
ENABLE_EMAIL_NOTIFICATIONS=false
```

### 2. Test with MailHog (Local Testing)
```bash
# Run MailHog in Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Configure .env
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
ENABLE_EMAIL_NOTIFICATIONS=true

# View emails at http://localhost:8025
```

### 3. Run Unit Tests
```bash
docker-compose exec api pytest tests/test_email_notifications.py -v
```

### 4. Manual Test
```bash
# Create a test booking
curl -X POST "http://localhost:8000/api/v1/bookings/" \
  -H "X-Tenant-Slug: acme-corp" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "start_time": "2026-02-10T10:00:00",
    "end_time": "2026-02-10T11:00:00",
    "customer_name": "Test Customer",
    "customer_email": "test@example.com",
    "notes": "Test booking"
  }'

# Check your email inbox for confirmation
```

## Troubleshooting

### Emails Not Sending

1. **Check SMTP credentials:**
   ```bash
   docker-compose exec api python -c "from api.core.config import settings; print(f'SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}, User: {settings.SMTP_USER}')"
   ```

2. **Check feature flag:**
   ```bash
   docker-compose exec api python -c "from api.core.config import settings; print(f'Email enabled: {settings.ENABLE_EMAIL_NOTIFICATIONS}')"
   ```

3. **Check application logs:**
   ```bash
   docker-compose logs api | grep -i email
   ```

4. **Test SMTP connection:**
   ```python
   # Run in container
   docker-compose exec api python
   
   >>> import smtplib
   >>> server = smtplib.SMTP('smtp.gmail.com', 587)
   >>> server.starttls()
   >>> server.login('your-email@gmail.com', 'your-app-password')
   >>> server.quit()
   ```

### Gmail "Less Secure Apps" Error

Gmail no longer supports "less secure apps". You **must** use an App Password with 2FA enabled.

### Port Blocked

If port 587 is blocked, try:
- Port 465 (SSL): `SMTP_PORT=465` (requires code changes for SSL)
- Port 25 (usually blocked by ISPs)

### Emails Going to Spam

To improve deliverability:
1. Use a custom domain for `FROM_EMAIL`
2. Set up SPF, DKIM, and DMARC records
3. Use a dedicated email service (SendGrid, Mailgun)
4. Warm up your sending domain gradually

## Production Recommendations

### 1. Use a Dedicated Email Service
- **SendGrid** - 100 emails/day free
- **Mailgun** - 5,000 emails/month free
- **Amazon SES** - 62,000 emails/month free (if hosted on AWS)

### 2. Set Up Email Monitoring
- Track delivery rates
- Monitor bounce rates
- Set up alerts for failures

### 3. Implement Email Queue (Future Enhancement)
For high-volume scenarios:
- Use Celery or RQ for async email sending
- Implement retry logic
- Add email delivery status tracking

### 4. Customize Templates Per Tenant
Future enhancement to allow each tenant to:
- Customize email branding
- Add their logo
- Modify email copy
- Set custom from address

## Security Notes

- Never commit `.env` file with real credentials
- Use app-specific passwords, not main account passwords
- Rotate SMTP credentials regularly
- Use environment variables for all sensitive data
- Consider using secret management (AWS Secrets Manager, HashiCorp Vault)

## Email Template Customization

Email templates are in `api/services/email_service.py`. To customize:

1. Modify HTML in `send_booking_confirmation_to_customer()`
2. Modify HTML in `send_booking_notification_to_business()`
3. Update plain text fallbacks
4. Test changes thoroughly

Future enhancement: Move templates to separate files or database for easier customization.
