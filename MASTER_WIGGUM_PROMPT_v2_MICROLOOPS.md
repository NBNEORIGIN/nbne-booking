# MASTER_WIGGUM_PROMPT_v2_MICROLOOPS.md

WIGGUM MODE: MICRO-LOOPS. DO NOT ASK TO CONTINUE.

## Objective

Build a moveable, local-server hosted, multi-tenant booking platform.

## Core Features

-   Configurable frontends (calendar/list/slot/form)
-   Branding per tenant
-   Staff support
-   Email + SMS reminders
-   CRM-lite
-   GDPR + Security
-   Client portal

## Hosting

-   Docker Compose
-   Local server / spare PC
-   Pathless routing

## Non-Negotiables

-   One codebase
-   Config-driven
-   Encrypted backups
-   Tenant isolation
-   No hardcoded secrets

------------------------------------------------------------------------

## Micro-Loops

### 0.1 Task Map

Create /docs/TASK_MAP.md

### 0.2 Local Dev

Docker compose + mailhog + postgres

### 0.3 Pathless Routing

No subpaths

### 1.1 Tenancy

Hostname-based tenant resolution

### 1.2 Config

Branding + behaviour schema

### 1.3 DB Scoping

tenant_id everywhere

### 2.1 Booking Primitives

Services, staff, availability

### 2.2 Slot API

Appointment slot generation

### 2.3 Session API

Class/session listing

### 3.1 UI Classes

List view for classes

### 3.2 UI Appointments

Slot picker

### 3.3 UI States

Empty/loading/error/sold-out

### 4.1 Email

Confirmations + reminders

### 4.2 SMS

Feature-flagged scaffold

### 5.1 Client Portal

Bookings + closures

### 5.2 CSV Export

Bookings + clients

### 5.3 CRM-lite

Consent + history

### 6.1 Security

Auth, sessions, rate limits

### 6.2 GDPR

DSAR, deletion, retention

### 7.1 Backup/Restore

Encrypted + drill

------------------------------------------------------------------------

## Exit Checklist

-   Local dev works
-   Two tenants seeded
-   Booking flows work
-   Email + SMS ready
-   Portal complete
-   GDPR + Security complete
-   Restore tested
