# NBNE Booking - Frontend Branding Scope

**Created:** February 2, 2026  
**Status:** LOOP 0 - Foundation & Scope  
**Implementation Path:** Server-rendered templates with Jinja2 + Tailwind CSS

---

## 🎯 OBJECTIVE

Create a customizable, branded public booking frontend for the NBNE Booking platform that supports multiple tenants with unique branding WITHOUT requiring per-client code forks.

**One codebase, many tenants.**

---

## ✅ IN SCOPE

### 1. Branding Configuration System
- **Tenant branding fields** (stored in database):
  - `client_display_name` - Override for public-facing name
  - `logo_url` - URL or path to logo image
  - `primary_color` - Main brand color (hex)
  - `secondary_color` - Optional secondary color (hex)
  - `accent_color` - Optional accent/CTA color (hex)
  - `booking_page_title` - Custom page title
  - `booking_page_intro` - Short introductory text
  - `location_text` - Business location (optional)
  - `contact_email` - Public contact email (optional)
  - `contact_phone` - Public contact phone (optional)
  - `business_address` - Full address (optional)
  - `social_links` - JSON object for social media links (optional)

### 2. Design System
- **Base layout components**:
  - Branded header with logo and client name
  - Consistent typography and spacing
  - Responsive grid system
  - Mobile-first approach
- **Color system**:
  - Automatic text contrast calculation (dark/light text on brand colors)
  - Accessible color combinations (WCAG AA minimum)
  - Safe fallbacks for invalid/missing colors
- **Component library**:
  - Buttons (primary, secondary, outline)
  - Form inputs and validation
  - Cards and containers
  - Status badges
  - Loading states

### 3. Public Booking Flow (4 Pages)
- **Page 1: Service Selection** (`/{tenant}/book` or `subdomain.domain.com/book`)
  - Display available services with descriptions
  - Show pricing if configured
  - Filter/search if multiple services
- **Page 2: Time Slot Selection**
  - Calendar/date picker
  - Available time slots based on availability rules
  - Show duration and service details
- **Page 3: Customer Details + Confirmation**
  - Form: name, email, phone, notes
  - Review selected service and time
  - Terms acceptance (if configured)
- **Page 4: Confirmation**
  - Booking reference number
  - Summary of booking
  - Add to calendar option
  - Contact information

### 4. Admin Branding Management
- **New admin page**: `/admin/branding`
  - Form to edit all branding fields
  - Color picker for hex colors
  - Logo URL input (no file upload in MVP)
  - Live preview panel showing booking page
  - Save and apply changes
- **Validation**:
  - Hex color format validation
  - URL validation for logo
  - Character limits on text fields

### 5. Documentation
- `docs/FRONTEND_BRANDING_SCOPE.md` (this file)
- `docs/WIGGUM_LOOP_LOG.md` - Loop execution log
- `docs/BRANDING_GUIDE.md` - How to configure tenant branding
- `docs/decisions.md` - Technical decisions and rationale

---

## ❌ OUT OF SCOPE

### Explicitly NOT Included (Anti-Creep)
- ❌ Payment processing or checkout
- ❌ Calendar sync (Google Calendar, iCal, etc.)
- ❌ Analytics or tracking dashboards
- ❌ SMS/email marketing campaigns
- ❌ Customer messaging or chat
- ❌ Multi-language support (English only for MVP)
- ❌ Advanced media management (file uploads, image editing)
- ❌ Custom CSS injection per tenant
- ❌ White-label domain management (DNS configuration)
- ❌ Mobile app (web-only)
- ❌ Booking modifications/cancellations (future feature)
- ❌ Waitlist functionality
- ❌ Group bookings
- ❌ Recurring bookings
- ❌ Staff management UI
- ❌ Reporting and exports

---

## 🏗️ IMPLEMENTATION PATH DECISION

### **CHOSEN: Server-Rendered Templates (Jinja2) + Tailwind CSS**

**Rationale:**
1. **Backend is already Python/FastAPI** - natural fit
2. **Templates already exist** for admin UI - proven pattern
3. **Simplest deployment** - no separate frontend build/deploy
4. **Fastest development** - leverage existing middleware and context
5. **SEO-friendly** - server-rendered HTML
6. **No CORS complexity** - same origin as API
7. **Tenant resolution already works** - middleware handles it

**Rejected Alternatives:**
- ❌ **Separate Next.js/React frontend**: Adds complexity, separate deployment, CORS, build pipeline
- ❌ **Vue/Nuxt**: Same issues as React, less familiar to team
- ❌ **Static site generator**: Can't handle dynamic tenant branding without rebuild

### Technology Stack
- **Backend**: FastAPI (existing)
- **Templates**: Jinja2 (existing)
- **CSS Framework**: Tailwind CSS (via CDN for MVP, build step later)
- **JavaScript**: Vanilla JS for interactivity (minimal)
- **Icons**: Heroicons or similar (via CDN)

---

## 📋 ACCEPTANCE CRITERIA

### Must Be True Before Exit:
- [ ] Tenant branding configuration exists in database with sensible defaults
- [ ] Public booking pages render with tenant-specific branding (name, logo, colors)
- [ ] Branding cannot break layout (safe fallbacks for missing/invalid data)
- [ ] Admin can update branding via `/admin/branding` page
- [ ] Admin can preview branding changes before saving
- [ ] Complete booking flow works end-to-end (4 pages)
- [ ] Mobile-responsive (works on phone screens)
- [ ] Basic accessibility (keyboard navigation, contrast, semantic HTML)
- [ ] All documentation complete (scope, guide, log, decisions)
- [ ] Deployed to VPS and verified working
- [ ] No per-client code forks or custom branches

---

## 🔍 CURRENT BACKEND AUDIT FINDINGS

### Tenant Resolution (✅ Already Implemented)
- **Middleware**: `TenantMiddleware` resolves tenant on every request
- **Resolution priority**:
  1. Subdomain (e.g., `client1.nbnebookings.co.uk`)
  2. X-Tenant-Slug header
  3. Path parameter (via route dependencies)
- **Context**: Tenant stored in `request.state.tenant` and context var
- **Database**: `tenants` table with `slug`, `subdomain`, `name`, `email`, `phone`, `is_active`, `settings` (JSON)

### Existing Infrastructure
- **Templates**: Jinja2 templates already used for admin UI (`api/templates/`)
- **Base template**: `base.html` with header, nav, styling
- **Admin routes**: `/admin/bookings`, `/admin/services`, `/admin/availability`
- **Tenant API**: Full CRUD at `/api/v1/tenants/`

### What Needs Adding
1. **Branding fields** - Add to tenant model or settings JSON
2. **Public routes** - New routes for `/{tenant}/book/*` or subdomain booking flow
3. **Public templates** - New templates for booking pages (separate from admin)
4. **Branding admin page** - New `/admin/branding` route and template
5. **Color utilities** - Helper functions for contrast calculation

---

## 📐 DATA MODEL STRATEGY

### Option A: Add Columns to Tenant Table (RECOMMENDED)
**Pros:**
- Explicit schema, type-safe
- Easy to query and validate
- Clear in database schema
- Better for future features (indexes, constraints)

**Cons:**
- Requires migration
- Less flexible for ad-hoc fields

### Option B: Use Existing `settings` JSON Column
**Pros:**
- No migration needed immediately
- Flexible for experimentation

**Cons:**
- No type safety
- Harder to query
- Validation must be in code
- Less discoverable

**DECISION: Use Option A (new columns) for core branding fields.**
- Branding is core functionality, not optional settings
- Type safety and validation are important
- Migration is acceptable for production-ready feature

---

## 🎨 BRANDING DEFAULTS

If tenant has not configured branding, use these defaults:

```python
DEFAULT_BRANDING = {
    "client_display_name": tenant.name,  # Use tenant name
    "logo_url": None,  # No logo, show text only
    "primary_color": "#2196F3",  # Material Blue
    "secondary_color": "#1976D2",  # Darker blue
    "accent_color": "#4CAF50",  # Green for CTAs
    "booking_page_title": f"Book with {tenant.name}",
    "booking_page_intro": "Select a service and time to book your appointment.",
    "location_text": None,
    "contact_email": tenant.email,  # Use tenant email
    "contact_phone": tenant.phone,  # Use tenant phone
    "business_address": None,
    "social_links": {}
}
```

---

## 🚀 WIGGUM LOOP SEQUENCE

1. **LOOP 0** - Foundation & Scope ✅ (this document)
2. **LOOP 1** - Branding Data Model (add fields, migration, defaults)
3. **LOOP 2** - Design System + Base Layout (branded shell, color system)
4. **LOOP 3** - Public Booking Flow UI (4 pages, wire to API)
5. **LOOP 4** - Branding Admin Page (edit form, preview, save)
6. **LOOP 5** - Polish + Responsive + Accessibility (mobile, a11y, UX)
7. **LOOP 6** - Deploy + Docs + Exit Gate (guide, deploy, verify)

---

## 📊 SUCCESS METRICS

- **Functional**: Booking flow works for any tenant with custom branding
- **Performance**: Pages load in < 2s on 3G
- **Accessibility**: WCAG AA contrast ratios, keyboard navigable
- **Maintainability**: No per-client code, single codebase
- **Documentation**: Complete guide for adding new tenants

---

**Next Step:** Create `docs/WIGGUM_LOOP_LOG.md` and begin LOOP 1 - Branding Data Model.
