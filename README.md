# NBNE Booking Platform

Managed booking system for NBNE client websites.

## 🚀 Live Deployment

**Production URL**: https://booking.nbnesigns.co.uk
- **Public Booking Form**: https://booking.nbnesigns.co.uk/
- **Admin Dashboard**: https://booking.nbnesigns.co.uk/admin.html
- **API Documentation**: https://booking.nbnesigns.co.uk/api/v1/docs

**Status**: ✅ **LIVE AND OPERATIONAL**

## Features

### Public Booking Form
- Service selection (Sign Installation, Maintenance, Repair, Site Survey)
- Customer information capture (name, email, phone)
- Date and time selection
- Automatic email notifications to sales@nbnesigns.co.uk
- Bookings saved with "confirmed" status

### Admin Dashboard
- Secure login with JWT authentication
- View all bookings in sortable table
- Filter by date range and status
- Export bookings to CSV
- Responsive design with Tailwind CSS

### Backend API
- Public booking endpoint (no authentication)
- Protected admin endpoints (JWT required)
- CSV export functionality
- Email notifications via IONOS SMTP
- Audit logging for all actions
- Rate limiting and CSRF protection

## Production Configuration

### Server Details
- **Host**: 87.106.65.142 (Ubuntu VPS)
- **Domain**: booking.nbnesigns.co.uk
- **SSL**: Automatic HTTPS via Caddy
- **Database**: PostgreSQL 15 (nbne_main)
- **Email**: IONOS SMTP (sales@nbnesigns.co.uk)

### Admin Credentials
- **Email**: admin@nbnesigns.co.uk
- **Password**: Admin123!
- **Role**: superadmin

### Environment
- **Tenant**: NBNE Signs (ID: 1)
- **Services**: 4 active services configured
- **SMTP**: IONOS (smtp.ionos.co.uk:587)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Local Development

1. **Clone and navigate to the repository**
   ```bash
   cd "g:/My Drive/003 APPS/024 BOOKING"
   ```

2. **Start the application**
   ```bash
   docker-compose up
   ```

3. **Access the application**
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/health
   - API Docs: http://localhost:8000/docs

### Running Migrations

```bash
# Create a new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1
```

## Project Structure

```
.
├── api/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Core configuration
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── main.py            # Application entry point
├── alembic/               # Database migrations
├── docs/                  # Documentation
│   ├── BOOKING_SCOPE.md   # MVP scope definition
│   ├── WIGGUM_LOOP_LOG.md # Development progress log
│   ├── RELEASE_CHECKLIST.md
│   └── decisions.md       # Architecture decisions
├── infra/                 # Infrastructure configs
│   └── .env.example       # Environment variables template
├── apps/                  # App registry
│   └── registry.json      # Application metadata
├── docker-compose.yml     # Local development setup
└── Dockerfile             # Container definition
```

## Development Workflow

This project follows the **Wiggum Loop** process:
- See `docs/WIGGUM_LOOP_LOG.md` for current progress
- Each loop must pass acceptance criteria before proceeding
- All decisions documented in `docs/decisions.md`

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Frontend**: Vanilla JavaScript with Tailwind CSS
- **Reverse Proxy**: Caddy 2 (automatic HTTPS)
- **Email**: IONOS SMTP
- **Deployment**: Docker Compose on Ubuntu VPS

## Documentation

- [Scope](docs/BOOKING_SCOPE.md) - What's in and out of scope
- [Wiggum Loop Log](docs/WIGGUM_LOOP_LOG.md) - Development progress
- [Release Checklist](docs/RELEASE_CHECKLIST.md) - Deployment procedures
- [Decisions](docs/decisions.md) - Architecture decisions

## Status

**Status**: ✅ **PRODUCTION - LIVE**  
**Version**: 1.0.0  
**Last Updated**: February 3, 2026

### Deployed Components
- ✅ Public booking form with email notifications
- ✅ Admin dashboard with login and CSV export
- ✅ Backend API with authentication
- ✅ PostgreSQL database with migrations applied
- ✅ HTTPS with automatic SSL certificates
- ✅ Email notifications via IONOS SMTP

### Ready For
- Client demonstrations
- Live customer bookings
- Multi-tenant expansion
- Additional features (blackouts, availability management)

## Key Files

- `/frontend/index.html` - Public booking form
- `/frontend/admin.html` - Admin dashboard
- `/api/api/v1/endpoints/bookings.py` - Booking endpoints (includes public and CSV export)
- `/api/core/csrf.py` - CSRF protection with exempt paths
- `/srv/booking/.env` - Production environment variables (on server)
- `/srv/booking/docker-compose.yml` - Production Docker configuration (on server)
