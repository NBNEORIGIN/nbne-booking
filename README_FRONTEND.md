# NBNE Booking - Frontend Branding System

## Overview

A customizable, multi-tenant booking frontend with per-client branding support. Built with server-rendered Jinja2 templates and Tailwind CSS for simplicity and maintainability.

## Features

✅ **Multi-Tenant Branding**
- Custom colors (primary, secondary, accent)
- Custom logo and display name
- Custom welcome messages
- Custom contact information
- Per-tenant configuration via database

✅ **Public Booking Flow**
- 4-step booking process
- Service selection with pricing
- Time slot selection with availability
- Customer details form
- Booking confirmation

✅ **Admin Interface**
- Branding editor with live preview
- Real-time color preview
- Form validation
- Easy-to-use interface

✅ **Accessibility**
- WCAG AA compliant
- Automatic color contrast calculation
- Keyboard navigation support
- Screen reader friendly
- Mobile responsive

✅ **Design System**
- Reusable UI components
- Consistent styling
- Tailwind CSS utilities
- CSS custom properties for theming

## Quick Start

### 1. Setup Database

```bash
# Apply migrations
docker exec booking-app alembic upgrade head
```

### 2. Create a Tenant

```bash
curl -X POST http://localhost:8000/api/v1/tenants/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "demo",
    "name": "Demo Company",
    "email": "demo@example.com",
    "primary_color": "#FF5722"
  }'
```

### 3. View Booking Page

Add header `X-Tenant-Slug: demo` and visit:
- Preview: `http://localhost:8000/public/preview`
- Booking: `http://localhost:8000/public/book`

## Architecture

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy
- **Templates**: Jinja2
- **Styling**: Tailwind CSS (CDN)
- **Database**: PostgreSQL
- **Deployment**: Docker + Caddy

### Directory Structure

```
api/
├── templates/
│   ├── public/              # Public-facing pages
│   │   ├── base.html        # Base template with branding
│   │   ├── components.html  # Reusable UI components
│   │   ├── preview.html     # Branding preview
│   │   ├── book_step1_services.html
│   │   ├── book_step2_slots.html
│   │   ├── book_step3_details.html
│   │   └── book_step4_confirmation.html
│   └── admin/
│       └── branding.html    # Branding admin page
├── api/
│   ├── public/
│   │   └── routes.py        # Public routes
│   └── admin/
│       └── routes.py        # Admin routes
├── utils/
│   └── branding.py          # Color utilities
└── models/
    └── tenant.py            # Tenant model with branding
```

## Branding System

### Branding Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_display_name` | String | No | Display name in header |
| `logo_url` | String | No | URL to logo image |
| `primary_color` | String | Yes | Main brand color (hex) |
| `secondary_color` | String | No | Secondary color (auto if not set) |
| `accent_color` | String | No | CTA color (auto if not set) |
| `booking_page_title` | String | No | Page title |
| `booking_page_intro` | Text | No | Welcome message |
| `location_text` | String | No | Location display |
| `contact_email` | String | No | Public email |
| `contact_phone` | String | No | Public phone |
| `business_address` | Text | No | Full address |

### Color System

**Automatic Features:**
- Text color calculation for contrast (WCAG AA)
- Color variants (light/dark) for hover states
- CSS custom properties generation
- Accessibility validation

**Example:**
```python
# Primary color: #FF5722 (orange)
# System generates:
# - primary-light: #FF784E
# - primary-dark: #CC451B
# - primary-text: #000000 (black for contrast)
```

## Routes

### Public Routes (`/public`)

| Route | Description |
|-------|-------------|
| `/public/preview` | Branding preview page |
| `/public/book` | Step 1: Service selection |
| `/public/book/slots` | Step 2: Time slot selection |
| `/public/book/details` | Step 3: Customer details |
| `/public/book/confirmation` | Step 4: Confirmation |

### Admin Routes (`/admin`)

| Route | Description |
|-------|-------------|
| `/admin/branding` | Branding editor |
| `/admin/bookings` | Bookings management |
| `/admin/services` | Services management |
| `/admin/availability` | Availability management |

## Development

### Local Setup

```bash
# Start containers
docker compose up -d

# Apply migrations
docker exec booking-app alembic upgrade head

# Create test data
docker exec booking-app python scripts/create_preview_data.py

# View logs
docker logs booking-app -f
```

### Testing

```bash
# Test with curl
curl -H "X-Tenant-Slug: preview-demo" http://localhost:8000/public/preview

# Test in browser
# 1. Install ModHeader extension
# 2. Add header: X-Tenant-Slug: preview-demo
# 3. Visit: http://localhost:8000/public/book
```

## Documentation

- **[Branding Guide](docs/BRANDING_GUIDE.md)** - Complete branding reference
- **[Accessibility Checklist](docs/ACCESSIBILITY_CHECKLIST.md)** - WCAG compliance
- **[Responsive Design](docs/RESPONSIVE_DESIGN.md)** - Mobile responsiveness
- **[Deployment Guide](docs/FRONTEND_DEPLOYMENT.md)** - Production deployment
- **[WIGGUM Loop Log](docs/WIGGUM_LOOP_LOG.md)** - Development history

## Customization

### Edit Branding via Admin UI

1. Navigate to `/admin/branding`
2. Edit fields in form
3. See live preview update
4. Click "Save Changes"

### Edit Branding via API

```bash
curl -X PATCH http://localhost:8000/api/v1/tenants/1 \
  -H "Content-Type: application/json" \
  -d '{
    "primary_color": "#9C27B0",
    "client_display_name": "My Business"
  }'
```

### Edit Branding via Database

```sql
UPDATE tenants 
SET primary_color = '#9C27B0',
    client_display_name = 'My Business'
WHERE id = 1;
```

## Accessibility

✅ **WCAG 2.1 AA Compliant**
- Color contrast: 4.5:1 minimum
- Keyboard navigation: Full support
- Screen readers: Semantic HTML
- Mobile: Touch targets ≥ 44px
- Forms: Associated labels

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile Safari: iOS 12+
- Chrome Mobile: Latest

## Performance

- **Page Load**: < 2s on 3G
- **First Paint**: < 1s
- **Interactive**: < 2s
- **Lighthouse Score**: 90+

## Future Enhancements

- [ ] Tailwind build step for production
- [ ] Image upload for logos
- [ ] Social media links
- [ ] Custom CSS injection
- [ ] Theme presets
- [ ] Dark mode support
- [ ] Multi-language support

## Contributing

Follow WIGGUM LOOP methodology:
1. Audit existing code
2. Plan implementation
3. Build incrementally
4. Document decisions
5. Test thoroughly
6. Deploy safely

## License

Proprietary - NBNE Signs Ltd

## Support

- Email: support@nbnesigns.co.uk
- Documentation: `/docs`
- Issues: GitHub Issues
