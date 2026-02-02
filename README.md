# NBNE Booking MVP

Managed booking system for NBNE client websites.

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
- **Deployment**: Render (planned)

## Documentation

- [Scope](docs/BOOKING_SCOPE.md) - What's in and out of scope
- [Wiggum Loop Log](docs/WIGGUM_LOOP_LOG.md) - Development progress
- [Release Checklist](docs/RELEASE_CHECKLIST.md) - Deployment procedures
- [Decisions](docs/decisions.md) - Architecture decisions

## Status

**Current Loop**: 0 (Foundation)  
**Status**: In Development  
**Version**: 0.1.0-alpha
