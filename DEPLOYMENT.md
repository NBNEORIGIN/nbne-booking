# NBNE Booking Platform - Deployment Documentation

## 🎯 Current Status: FULLY DEPLOYED AND LIVE

**Production URL:** https://booking.nbnesigns.co.uk  
**Public Booking Form:** https://booking.nbnesigns.co.uk/  
**Admin Dashboard:** https://booking.nbnesigns.co.uk/admin.html  
**API Documentation:** https://booking.nbnesigns.co.uk/api/v1/docs  
**Health Check:** https://booking.nbnesigns.co.uk/health

---

## 📋 Deployment Summary

The NBNE Booking Platform has been successfully deployed to a VPS and is fully operational with:
- ✅ Public booking form with email notifications
- ✅ Admin dashboard with login and CSV export
- ✅ Backend API with JWT authentication
- ✅ Docker containerization
- ✅ PostgreSQL database with migrations
- ✅ HTTPS with automatic SSL certificates (Let's Encrypt via Caddy)
- ✅ DNS configured
- ✅ CORS and CSRF protection
- ✅ Email notifications via IONOS SMTP
- ✅ Auto-restart on server reboot
- ✅ Interactive API documentation (Swagger UI)

---

## 🖥️ VPS Configuration

### Server Details
- **IP Address:** `87.106.65.142`
- **OS:** Ubuntu 24.04
- **Domain:** `booking.nbnesigns.co.uk`
- **DNS Provider:** IONOS
- **SSH Access:** `ssh toby@87.106.65.142`

### Installed Software
- Docker & Docker Compose
- Caddy web server (reverse proxy + HTTPS)
- PostgreSQL 15 (running in Docker)

---

## 🐳 Docker Setup

### Containers
1. **booking-api** - FastAPI application
   - Port: 8000 (internal)
   - Network: booking-network
   - Auto-restart: unless-stopped

2. **booking-db** - PostgreSQL 15 database
   - Port: 5432 (internal only)
   - Network: booking-network
   - Volume: booking_db_data

3. **booking-caddy** - Caddy reverse proxy
   - Ports: 80, 443 (external)
   - Networks: booking-network, caddy-network
   - Serves frontend files from /srv/booking/frontend
   - Proxies API requests to booking-api:8000

### Docker Networks
- **booking-network** - Backend communication
- **caddy-network** - Frontend/proxy communication

---

## 📁 File Structure on VPS

```
/srv/booking/
├── api/                          # FastAPI application code
│   ├── api/v1/endpoints/         # API endpoints
│   │   ├── bookings.py          # Booking endpoints (public + CSV export)
│   │   ├── services.py          # Service endpoints (public)
│   │   └── auth.py              # Authentication endpoints
│   ├── core/                    # Core configuration
│   │   ├── csrf.py              # CSRF protection
│   │   └── config.py            # Settings
│   ├── models/                  # SQLAlchemy models
│   └── main.py                  # Application entry point
├── alembic/                     # Database migrations
├── frontend/                    # Frontend HTML files
│   ├── index.html              # Public booking form
│   └── admin.html              # Admin dashboard
├── docker-compose.yml          # Docker Compose configuration
├── Caddyfile                   # Caddy reverse proxy configuration
├── Dockerfile                  # Application container definition
└── .env                        # Environment variables (NOT in git)
```

---

## 🔐 Credentials & Configuration

### Database
- **Host:** `booking-db` (Docker container name)
- **Port:** `5432`
- **Database:** `nbne_main`
- **User:** `nbne_admin`
- **Password:** (stored in .env file)

### Admin Credentials
- **Email:** `admin@nbnesigns.co.uk`
- **Password:** `Admin123!`
- **Role:** superadmin
- **Tenant ID:** 1 (NBNE Signs)

### Environment Variables (`/srv/booking/.env`)
```bash
# Database
POSTGRES_SERVER=db
POSTGRES_USER=nbne_admin
POSTGRES_PASSWORD=<password>
POSTGRES_DB=nbne_main
POSTGRES_PORT=5432

# Application
SECRET_KEY=<secret_key>
BACKEND_CORS_ORIGINS=https://booking.nbnesigns.co.uk

# Email (IONOS SMTP)
SMTP_HOST=smtp.ionos.co.uk
SMTP_PORT=587
SMTP_USER=sales@nbnesigns.co.uk
SMTP_PASSWORD=!49Monkswood
SMTP_FROM_EMAIL=sales@nbnesigns.co.uk
SMTP_FROM_NAME=NBNE Booking
```

**Note:** Email notifications are sent to `sales@nbnesigns.co.uk` when bookings are submitted.

### Caddy Configuration (`/srv/booking/Caddyfile`)
```caddyfile
booking.nbnesigns.co.uk {
    # Serve frontend files
    root * /srv/booking/frontend
    file_server
    
    # Proxy API requests to backend
    reverse_proxy /api/* api:8000
    
    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
    
    encode gzip
}
```

---

## 🗄️ Database Schema

### Tables Created (via Alembic migrations)
1. **tenants** - Multi-tenant support (ID 1 = NBNE Signs)
2. **users** - Admin users with authentication
3. **services** - Bookable services (4 active services)
4. **availability** - Service availability schedules
5. **blackouts** - Blocked time periods
6. **bookings** - Customer bookings
7. **audit_logs** - Audit trail for all actions

### Current Data
- **Tenant:** NBNE Signs (ID: 1)
- **Admin User:** admin@nbnesigns.co.uk (superadmin)
- **Services:** 4 active services configured
  - Sign Installation (120 min, £250)
  - Sign Maintenance (60 min, £75)
  - Sign Repair (90 min, £150)
  - Site Survey (45 min, £50)

### Migration Status
All migrations applied and up to date.

---

## 🔧 Common Commands

### Application Management
```bash
# Navigate to booking directory
cd /srv/booking

# Start application
docker compose up -d

# Stop application
docker compose down

# View logs
docker compose logs api
docker compose logs api -f  # Follow logs

# Restart API (useful for rate limit reset)
docker compose restart api

# Rebuild API after code changes
docker compose build api
docker compose up -d api

# Rebuild API without cache (force fresh build)
docker compose build api --no-cache
docker compose up -d api
```

### Update Frontend Files
```powershell
# From Windows PowerShell
scp "g:\My Drive\003 APPS\024 BOOKING\frontend\index.html" toby@87.106.65.142:/srv/booking/frontend/index.html
scp "g:\My Drive\003 APPS\024 BOOKING\frontend\admin.html" toby@87.106.65.142:/srv/booking/frontend/admin.html

# No restart needed - Caddy serves files directly
```

### Update Backend Code
```powershell
# From Windows PowerShell - upload specific file
scp "g:\My Drive\003 APPS\024 BOOKING\api\api\v1\endpoints\bookings.py" toby@87.106.65.142:/srv/booking/api/api/v1/endpoints/bookings.py
```

```bash
# On server - rebuild and restart API
cd /srv/booking
docker compose build api
docker compose up -d api

# Verify API is running
docker compose ps
docker compose logs api --tail 20
```

### Database Operations
```bash
# Run migrations
docker compose exec api alembic upgrade head

# Access PostgreSQL shell
docker compose exec db psql -U nbne_admin -d nbne_main

# View users
docker compose exec db psql -U nbne_admin -d nbne_main -c "SELECT email, role FROM users;"

# View bookings
docker compose exec db psql -U nbne_admin -d nbne_main -c "SELECT id, customer_name, customer_email, service_id, start_time, status FROM bookings;"

# Backup database
docker compose exec db pg_dump -U nbne_admin nbne_main > backup_$(date +%Y%m%d).sql

# Restore database
cat backup.sql | docker compose exec -i db psql -U nbne_admin -d nbne_main
```

### Caddy Management
```bash
# Caddy runs in Docker container
# Restart Caddy
docker compose restart caddy

# View Caddy logs
docker compose logs caddy

# Reload Caddyfile after changes
docker compose restart caddy
```

### System Monitoring
```bash
# Check container status
docker ps

# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory usage
free -h

# Check system logs
sudo journalctl -xe
```

---

## 🚀 Deployment Process (For Future Updates)

### 1. Update Frontend Files
```powershell
# From Windows PowerShell
scp "g:\My Drive\003 APPS\024 BOOKING\frontend\index.html" toby@87.106.65.142:/srv/booking/frontend/index.html
scp "g:\My Drive\003 APPS\024 BOOKING\frontend\admin.html" toby@87.106.65.142:/srv/booking/frontend/admin.html
# Changes take effect immediately
```

### 2. Update Backend Code
```powershell
# Upload changed file(s)
scp "g:\My Drive\003 APPS\024 BOOKING\api\api\v1\endpoints\bookings.py" toby@87.106.65.142:/srv/booking/api/api/v1/endpoints/bookings.py
```

```bash
# SSH into VPS
ssh toby@87.106.65.142

# Rebuild and restart API
cd /srv/booking
docker compose build api
docker compose up -d api

# Verify deployment
docker compose ps
docker compose logs api --tail 20
curl https://booking.nbnesigns.co.uk/health
```

### 3. Run Migrations (if schema changed)
```bash
cd /srv/booking
docker compose exec api alembic upgrade head
```

### 4. Test Deployment
- Public form: https://booking.nbnesigns.co.uk/
- Admin dashboard: https://booking.nbnesigns.co.uk/admin.html
- API docs: https://booking.nbnesigns.co.uk/api/v1/docs

---

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker compose logs api --tail 50

# Check all container status
docker compose ps

# Check environment variables
docker compose exec api printenv | grep -E "POSTGRES|SMTP|CORS"

# Rebuild from scratch
cd /srv/booking
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database Connection Issues
```bash
# Test database connection
docker compose exec api python -c "from api.core.database import engine; print(engine.connect())"

# Check if postgres container is running
docker compose ps db

# Check database logs
docker compose logs db --tail 20

# Access database directly
docker compose exec db psql -U nbne_admin -d nbne_main
```

### HTTPS/SSL Issues
```bash
# Check Caddy logs
docker compose logs caddy --tail 50

# Test DNS resolution
nslookup booking.nbnesigns.co.uk

# Check if ports are exposed
docker compose ps caddy

# Restart Caddy
docker compose restart caddy

# Test HTTPS
curl -I https://booking.nbnesigns.co.uk
```

### Rate Limiting Issues
If login fails with "Too many requests" (429 error):
```bash
# Restart API to reset rate limit counters
cd /srv/booking
docker compose restart api
```

### Email Not Sending
```bash
# Check SMTP environment variables
docker compose exec api printenv | grep SMTP

# Check API logs for email errors
docker compose logs api --tail 50 | grep -i email

# Test SMTP connection manually
docker compose exec api python3 -c "
import smtplib, os
with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ['SMTP_PORT'])) as s:
    s.starttls()
    s.login(os.environ['SMTP_USER'], os.environ['SMTP_PASSWORD'])
    print('SMTP connection successful')
"
```

### Admin Login Issues
- Verify credentials: admin@nbnesigns.co.uk / Admin123!
- Check browser console for errors (F12)
- Try hard refresh (Ctrl+Shift+R)
- If rate limited, restart API: `docker compose restart api`

---

## 📊 API Endpoints

### Base URL
`https://booking.nbnesigns.co.uk/api/v1`

### Public Endpoints (No Authentication)

#### Services
- `GET /api/v1/services/public` - List active services for tenant

#### Bookings
- `POST /api/v1/bookings/public` - Create booking (public form)
  - Automatically assigns to tenant ID 1 (NBNE Signs)
  - Sends email notification to sales@nbnesigns.co.uk
  - Returns booking confirmation

### Protected Endpoints (Authentication Required)

#### Authentication
- `POST /api/v1/auth/login` - Login with email/password
  - Returns JWT access token
  - Token valid for 24 hours

#### Bookings
- `GET /api/v1/bookings/` - List all bookings (admin)
- `GET /api/v1/bookings/export` - Export bookings to CSV
- `GET /api/v1/bookings/{booking_id}` - Get booking details
- `PATCH /api/v1/bookings/{booking_id}` - Update booking
- `DELETE /api/v1/bookings/{booking_id}` - Cancel booking

#### Services (Admin)
- `GET /api/v1/services/` - List all services
- `POST /api/v1/services/` - Create service
- `PATCH /api/v1/services/{service_id}` - Update service
- `DELETE /api/v1/services/{service_id}` - Delete service

#### Other Endpoints
- Tenants, Availability, Blackouts, Slots (see API docs)

### Testing Endpoints
Visit https://booking.nbnesigns.co.uk/api/v1/docs for interactive API documentation.

---

## ✅ Completed Features

- ✅ Public booking form with service selection
- ✅ Admin dashboard with JWT authentication
- ✅ CSV export for bookings
- ✅ Email notifications via IONOS SMTP
- ✅ HTTPS with automatic SSL
- ✅ CSRF protection with exempt paths
- ✅ Rate limiting
- ✅ Audit logging
- ✅ Multi-tenant support (ready for expansion)

## 🔄 Future Enhancements

### High Priority
- [ ] Automated database backups
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Customer email confirmations
- [ ] Booking cancellation/rescheduling
- [ ] Calendar view for available slots

### Medium Priority
- [ ] SMS notifications
- [ ] Payment integration
- [ ] Admin booking creation
- [ ] Blackout period management UI
- [ ] Availability schedule management UI

### Low Priority
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Mobile app
- [ ] Customer portal
- [ ] Analytics dashboard

---

## 📝 Important Notes

### CSRF Protection
- Public endpoints (`/services/public`, `/bookings/public`) are CSRF-exempt
- Auth endpoints (`/auth/login`, `/auth/register`) are CSRF-exempt
- All other POST/PUT/PATCH/DELETE requests require CSRF token

### Email Configuration
- Using IONOS SMTP (smtp.ionos.co.uk:587)
- Emails sent from sales@nbnesigns.co.uk
- Admin receives notification for each booking
- SMTP credentials stored in .env file

### Rate Limiting
- Protects against brute force attacks
- Can cause login issues if too many attempts
- Reset by restarting API container

### Admin Password Reset
```bash
# Create password reset script
cat > /tmp/reset_password.py << 'EOF'
import sys
sys.path.insert(0, '/app')
from api.core.database import SessionLocal
from api.models.user import User
from api.core.security import get_password_hash

db = SessionLocal()
admin = db.query(User).filter(User.email == 'admin@nbnesigns.co.uk').first()
if admin:
    admin.hashed_password = get_password_hash('Admin123!')
    db.commit()
    print('Password reset successfully')
db.close()
EOF

# Run script
docker cp /tmp/reset_password.py booking-api:/tmp/
docker compose exec api python3 /tmp/reset_password.py
```

### SSL Certificates
- Automatically obtained and renewed by Caddy
- Stored in Docker volume `caddy_data`
- No manual intervention required

---

## 🔗 Useful Links

- **Public Booking Form:** https://booking.nbnesigns.co.uk/
- **Admin Dashboard:** https://booking.nbnesigns.co.uk/admin.html
- **API Docs:** https://booking.nbnesigns.co.uk/api/v1/docs
- **Health Check:** https://booking.nbnesigns.co.uk/health
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Caddy Documentation:** https://caddyserver.com/docs/

---

## 📞 Support Information

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker logs booking-app`
3. Check Caddy logs: `sudo journalctl -u caddy -f`
4. Review this documentation
5. Check the GitHub repository for updates

---

**Last Updated:** February 3, 2026  
**Deployment Status:** ✅ **LIVE IN PRODUCTION**  
**Version:** 1.0.0

## 🎉 Platform Ready For

- ✅ Client demonstrations
- ✅ Live customer bookings
- ✅ Multi-tenant expansion (squash courts, etc.)
- ✅ Additional feature development
