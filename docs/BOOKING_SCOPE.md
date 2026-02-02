# NBNE Booking - MVP Scope

## Overview
Managed-booking feature bundled with NBNE client websites (NOT a public Calendly competitor).

## In Scope

### Tenancy
- Tenant identified by slug or subdomain
- Strict isolation between tenants

### Services
- CRUD operations (name, duration, optional price)

### Availability
- Weekly windows (e.g., Mon-Fri 9am-5pm)
- Blackouts (specific dates/times unavailable)

### Slot Generation
- Returns available slots for service + date range
- Respects availability windows and blackouts
- Handles varying service durations

### Bookings
- Create booking (name, email, optional phone)
- Status: confirmed/cancelled
- Server-side prevention of double booking

### Notifications
- **Email (required)**: Confirmation to customer + business
- **SMS (optional)**: Behind feature flag; provider TBD; must be possible to run without SMS

### Admin UI
- Login/authentication
- Manage services, availability, blackouts
- View bookings list
- Export bookings to CSV

### Security
- Rate limiting
- Honeypot fields
- Input validation

### Operations
- Nightly DB backup
- Documented restore procedure
- Basic health endpoint
- Logging

## Non-Goals (Out of Scope)
- Payments/billing integration
- Two-way calendar sync
- Complex rostering/staff scheduling
- Public self-signup for new tenants
- Mobile apps
- Advanced reporting/analytics
- Multi-language support (MVP is English only)
- Recurring appointments
- Waitlist functionality

## Technical Constraints
- No bespoke per-client code; configuration only
- Feature flags for optional functionality
- Small, composable changes (no large refactors)
