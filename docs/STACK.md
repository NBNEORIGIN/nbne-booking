# NBNE Booking — Stack Documentation

**Generated:** 2026-02-02  
**Target:** VPS Production Deployment (booking-beta.nbnesigns.co.uk)

---

## Application Stack

### Framework
- **FastAPI** 0.109.0
- **Python** 3.11-slim
- **ASGI Server:** Uvicorn 0.27.0 with uvloop

### Database
- **PostgreSQL** (external container: `nbne-postgres`)
- **ORM:** SQLAlchemy 2.0.25
- **Migrations:** Alembic 1.13.1
- **Driver:** psycopg2-binary 2.9.9

### Features
- Multi-tenant architecture (subdomain/slug/header-based)
- RESTful API (`/api/v1/`)
- Admin UI (`/admin/`) with Jinja2 templates
- Email notifications (SMTP)
- Health endpoint (`/health`)

---

## Runtime Configuration

### Entry Command
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Required Environment Variables

**Database (use DATABASE_URL for VPS):**
```bash
DATABASE_URL=postgresql://nbne_admin:PASSWORD@nbne-postgres:5432/nbne_main
```

**CORS:**
```bash
BACKEND_CORS_ORIGINS=https://booking-beta.nbnesigns.co.uk
```

**Email (optional):**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@nbnesigns.co.uk
FROM_NAME=NBNE Booking
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=false
```

### Ports
- **Application:** 8000 (configurable via `PORT` env var)
- **Health Check:** `GET /health`

---

## File Structure

```
/srv/booking/
├── app/                    # Git clone of repository
│   ├── api/               # FastAPI application
│   ├── alembic/           # Database migrations
│   ├── scripts/           # Utility scripts
│   ├── tests/             # Test suite
│   ├── Dockerfile         # Container definition
│   └── alembic.ini        # Migration config
├── docker/
│   └── docker-compose.yml # Production compose file
├── .env                   # Environment variables (SECRET)
└── docs/
    ├── STACK.md          # This file
    ├── DEPLOY.md         # Deployment guide (TBD)
    └── BACKUP_RESTORE.md # Backup procedures (TBD)
```

---

## Database Schema

**Migrations Location:** `/alembic/versions/`

**Tables (expected):**
- `tenants` - Multi-tenant configuration
- `services` - Bookable services
- `bookings` - Customer bookings
- `availability` - Service availability rules
- `alembic_version` - Migration tracking

**Migration Command:**
```bash
docker exec booking-app alembic upgrade head
```

---

## Dependencies

See `api/requirements.txt` for full list (18 packages).

**Key Dependencies:**
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- sqlalchemy==2.0.25
- psycopg2-binary==2.9.9
- pydantic==2.5.3
- alembic==1.13.1
- jinja2==3.1.2

---

## Logging

- **Format:** JSON-structured logs to stdout
- **Level:** INFO (configurable)
- **Collection:** Docker logs (`docker logs booking-app`)

---

## Health & Monitoring

**Health Endpoint:**
```bash
curl https://booking-beta.nbnesigns.co.uk/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "NBNE Booking API",
  "version": "0.1.0-alpha"
}
```

---

## Known Blockers (Resolved in LOOP 2)

1. ✅ Dockerfile production-ready
2. ⚠️ docker-compose.yml needs VPS adaptation (remove internal Postgres)
3. ⚠️ Missing .dockerignore
4. ⚠️ Missing VPS .env.example
5. ⚠️ Migration procedure not documented

---

**LOOP 1 STATUS:** ✅ COMPLETE  
**Next:** LOOP 2 — Containerisation for VPS
