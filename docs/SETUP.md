# Setup Guide

## Prerequisites

1. **Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop
   - Verify with: `docker --version`

2. **Git** (for version control)

## Initial Setup

### 1. Start Docker Desktop
Ensure Docker Desktop is running before proceeding.

### 2. Clone/Navigate to Repository
```bash
cd "g:/My Drive/003 APPS/024 BOOKING"
```

### 3. Configure Environment
Copy the example environment file:
```bash
cp infra/.env.example .env
```

For local development, the default values in `.env` are sufficient.

### 4. Start the Application
```bash
docker-compose up -d
```

This will:
- Pull the PostgreSQL image
- Build the FastAPI application image
- Start both containers
- Run database migrations (when configured)

### 5. Verify Installation

**Check container status:**
```bash
docker-compose ps
```

**Check health endpoint:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "NBNE Booking API",
  "version": "0.1.0-alpha"
}
```

**View API documentation:**
Open http://localhost:8000/docs in your browser

### 6. View Logs
```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f api

# Database only
docker-compose logs -f db
```

## Database Migrations

### Create a new migration
```bash
docker-compose exec api alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
docker-compose exec api alembic upgrade head
```

### Rollback last migration
```bash
docker-compose exec api alembic downgrade -1
```

### View migration history
```bash
docker-compose exec api alembic history
```

## Stopping the Application

```bash
# Stop containers (preserves data)
docker-compose stop

# Stop and remove containers (preserves volumes)
docker-compose down

# Stop, remove containers and volumes (deletes all data)
docker-compose down -v
```

## Troubleshooting

### Docker Desktop not running
**Error:** `unable to get image` or `cannot connect to Docker daemon`

**Solution:** Start Docker Desktop and wait for it to fully initialize.

### Port already in use
**Error:** `port is already allocated`

**Solution:** 
- Check what's using the port: `netstat -ano | findstr :8000`
- Stop the conflicting service or change the port in `docker-compose.yml`

### Database connection errors
**Error:** `could not connect to server`

**Solution:**
- Ensure the database container is healthy: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Wait for the health check to pass (can take 10-30 seconds on first start)

### Permission errors
**Error:** Permission denied when accessing files

**Solution:**
- Ensure Docker Desktop has access to the drive
- Check Docker Desktop Settings > Resources > File Sharing

## Development Workflow

1. Make code changes in the `api/` directory
2. Changes are automatically reloaded (hot reload enabled)
3. View logs to see the reload: `docker-compose logs -f api`
4. Test changes via http://localhost:8000

## Tenant Provisioning (Post-Loop 1)

Instructions for adding new tenants will be added after Loop 1 is completed.

## Production Deployment

See `docs/RELEASE_CHECKLIST.md` for production deployment procedures.
