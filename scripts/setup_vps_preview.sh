#!/bin/bash
# Setup preview data on VPS

echo "Creating preview tenant..."
curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/tenants/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "preview-demo",
    "name": "Preview Demo Company",
    "email": "demo@example.com",
    "phone": "+44 20 1234 5678",
    "client_display_name": "Preview Demo",
    "primary_color": "#FF5722",
    "secondary_color": "#E64A19",
    "accent_color": "#4CAF50",
    "booking_page_title": "Book Your Appointment",
    "booking_page_intro": "Welcome! Select a service and time that works for you.",
    "location_text": "London, UK",
    "contact_email": "bookings@previewdemo.com",
    "contact_phone": "+44 20 1234 5678"
  }'

echo -e "\n\nCreating services..."

# Service 1: Consultation
curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/services/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: preview-demo" \
  -d '{
    "name": "Consultation",
    "description": "30-minute consultation session",
    "duration_minutes": 30,
    "price": 50.00,
    "is_active": true
  }'

# Service 2: Full Service
curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/services/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: preview-demo" \
  -d '{
    "name": "Full Service",
    "description": "Comprehensive 60-minute service",
    "duration_minutes": 60,
    "price": 100.00,
    "is_active": true
  }'

# Service 3: Quick Check
curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/services/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: preview-demo" \
  -d '{
    "name": "Quick Check",
    "description": "15-minute quick check-up",
    "duration_minutes": 15,
    "price": 25.00,
    "is_active": true
  }'

echo -e "\n\nCreating availability (Mon-Fri, 9 AM - 5 PM)..."

# Monday-Friday availability
for day in {0..4}; do
  curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/availability/ \
    -H "Content-Type: application/json" \
    -H "X-Tenant-Slug: preview-demo" \
    -d "{
      \"day_of_week\": $day,
      \"start_time\": \"09:00:00\",
      \"end_time\": \"17:00:00\"
    }"
done

echo -e "\n\n✅ Preview data created!"
echo "Test at: https://booking-beta.nbnesigns.co.uk/public/preview"
echo "Booking: https://booking-beta.nbnesigns.co.uk/public/book"
echo "Header: X-Tenant-Slug: preview-demo"
