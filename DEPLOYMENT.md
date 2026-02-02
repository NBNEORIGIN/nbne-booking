# NBNE Booking API - Deployment Documentation

## 🎯 Current Status: FULLY DEPLOYED AND LIVE

**Live API URL:** https://booking-beta.nbnesigns.co.uk  
**API Documentation:** https://booking-beta.nbnesigns.co.uk/api/v1/docs  
**Health Check:** https://booking-beta.nbnesigns.co.uk/health

---

## 📋 Deployment Summary

The NBNE Booking API has been successfully deployed to a VPS and is fully operational with:
- ✅ Docker containerization
- ✅ PostgreSQL database with migrations
- ✅ HTTPS with automatic SSL certificates (Let's Encrypt via Caddy)
- ✅ DNS configured
- ✅ CORS enabled
- ✅ Auto-restart on server reboot
- ✅ Interactive API documentation (Swagger UI)

---

## 🖥️ VPS Configuration

### Server Details
- **IP Address:** `87.106.65.142`
- **OS:** Ubuntu 24.04
- **Domain:** `booking-beta.nbnesigns.co.uk`
- **DNS Provider:** IONOS

### Installed Software
- Docker & Docker Compose
- Caddy web server (reverse proxy + HTTPS)
- PostgreSQL 15 (running in Docker)

---

## 🐳 Docker Setup

### Containers
1. **booking-app** - FastAPI application
   - Port: 8000 (internal)
   - Network: nbne-network
   - Auto-restart: unless-stopped

2. **nbne-postgres** - PostgreSQL 15 database
   - Port: 5432 (internal only)
   - Network: nbne-network
   - Volume: postgres-data

### Docker Network
- **Name:** `nbne-network`
- **Type:** Bridge
- **External:** Yes (created manually)

---

## 📁 File Structure on VPS

```
/srv/booking/
├── app/                          # Git repository clone
│   ├── api/                      # FastAPI application code
│   ├── alembic/                  # Database migrations
│   ├── docker-compose.vps.yml    # VPS-specific compose file
│   ├── Dockerfile                # Application container definition
│   └── ...
├── docker/
│   └── docker-compose.yml        # Symlink to ../app/docker-compose.vps.yml
└── .env                          # Environment variables (NOT in git)

/etc/caddy/
└── Caddyfile                     # Caddy reverse proxy configuration
```

---

## 🔐 Credentials & Configuration

### Database
- **Host:** `nbne-postgres` (Docker container name)
- **Port:** `5432`
- **Database:** `nbne_main`
- **User:** `nbne_admin`
- **Password:** `Monkswood49` (changed from original `!49Monkswood` to avoid special char issues)

### Environment Variables (`/srv/booking/.env`)
```bash
# Database
DATABASE_URL=postgresql://nbne_admin:Monkswood49@nbne-postgres:5432/nbne_main

# CORS
BACKEND_CORS_ORIGINS=https://booking-beta.nbnesigns.co.uk

# Email (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=tbjp nioa dwgr tsno
FROM_EMAIL=your-email@gmail.com
FROM_NAME=NBNE Booking
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=false
```

### Caddy Configuration (`/etc/caddy/Caddyfile`)
```
booking-beta.nbnesigns.co.uk {
    reverse_proxy localhost:8000
    
    log {
        output file /var/log/caddy/booking-beta.log
        format json
    }
    
    encode gzip
}
```

---

## 🗄️ Database Schema

### Tables Created (via Alembic migrations)
1. **tenants** - Multi-tenant support
2. **services** - Bookable services
3. **availability** - Service availability schedules
4. **blackouts** - Blocked time periods
5. **bookings** - Customer bookings

### Migration Status
All migrations up to date. Last migration: `004` (create bookings table)

---

## 🔧 Common Commands

### Application Management
```bash
# Navigate to docker directory
cd /srv/booking/docker

# Start application
docker compose up -d

# Stop application
docker compose down

# View logs
docker logs booking-app
docker logs -f booking-app  # Follow logs

# Restart application
docker compose restart

# Rebuild and restart
docker compose down
docker compose up -d --build
```

### Update Application from Git
```bash
cd /srv/booking/app
git pull
cd /srv/booking/docker
docker compose down
docker compose up -d --build
```

### Database Operations
```bash
# Run migrations
docker exec booking-app alembic upgrade head

# Access PostgreSQL shell
docker exec -it nbne-postgres psql -U nbne_admin -d nbne_main

# Backup database
docker exec nbne-postgres pg_dump -U nbne_admin nbne_main > backup.sql

# Restore database
cat backup.sql | docker exec -i nbne-postgres psql -U nbne_admin -d nbne_main
```

### Caddy Management
```bash
# Reload Caddy configuration
sudo systemctl reload caddy

# Check Caddy status
sudo systemctl status caddy

# View Caddy logs
sudo journalctl -u caddy -f

# Test Caddyfile syntax
sudo caddy validate --config /etc/caddy/Caddyfile
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

### 1. Make Changes Locally
```bash
# Make code changes
# Test locally
git add .
git commit -m "Description of changes"
git push origin main
```

### 2. Deploy to VPS
```bash
# SSH into VPS
ssh toby@87.106.65.142

# Pull latest changes
cd /srv/booking/app
git pull

# Rebuild and restart
cd /srv/booking/docker
docker compose down
docker compose up -d --build

# Check logs
docker logs booking-app

# Test health endpoint
curl https://booking-beta.nbnesigns.co.uk/health
```

### 3. Run Migrations (if needed)
```bash
docker exec booking-app alembic upgrade head
```

---

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs booking-app

# Check if port is already in use
sudo netstat -tulpn | grep 8000

# Check environment variables
docker exec booking-app env | grep -E "DATABASE|CORS"

# Rebuild from scratch
docker compose down
docker compose up -d --build
```

### Database Connection Issues
```bash
# Test database connection
docker exec booking-app psql -U nbne_admin -h nbne-postgres -d nbne_main

# Check if postgres container is running
docker ps | grep postgres

# Check network connectivity
docker exec booking-app ping nbne-postgres
```

### HTTPS/SSL Issues
```bash
# Check Caddy logs
sudo journalctl -u caddy -f

# Test DNS resolution
nslookup booking-beta.nbnesigns.co.uk

# Check if port 443 is open
sudo netstat -tulpn | grep 443

# Reload Caddy
sudo systemctl reload caddy
```

### CORS Issues
The CORS configuration had issues with Pydantic trying to parse the string as JSON. This was fixed by:
1. Updating the validator in `api/core/config.py` to handle string input properly
2. Adding a custom `parse_env_var` method to prevent JSON parsing for BACKEND_CORS_ORIGINS

If CORS issues occur, ensure the `.env` file has:
```bash
BACKEND_CORS_ORIGINS=https://booking-beta.nbnesigns.co.uk
```
(No quotes, no brackets, just the plain URL)

---

## 📊 API Endpoints

### Base URL
`https://booking-beta.nbnesigns.co.uk/api/v1`

### Available Endpoints

#### Tenants
- `GET /api/v1/tenants/` - List all tenants
- `POST /api/v1/tenants/` - Create tenant
- `GET /api/v1/tenants/{tenant_id}` - Get tenant
- `PATCH /api/v1/tenants/{tenant_id}` - Update tenant
- `DELETE /api/v1/tenants/{tenant_id}` - Delete tenant
- `GET /api/v1/tenants/slug/{slug}` - Get tenant by slug

#### Services
- `GET /api/v1/services/` - List all services
- `POST /api/v1/services/` - Create service
- `GET /api/v1/services/{service_id}` - Get service
- `PATCH /api/v1/services/{service_id}` - Update service
- `DELETE /api/v1/services/{service_id}` - Delete service

#### Availability
- `GET /api/v1/availability/` - List availability schedules
- `POST /api/v1/availability/` - Create availability
- `GET /api/v1/availability/{availability_id}` - Get availability
- `PATCH /api/v1/availability/{availability_id}` - Update availability
- `DELETE /api/v1/availability/{availability_id}` - Delete availability

#### Blackouts
- `GET /api/v1/blackouts/` - List blackout periods
- `POST /api/v1/blackouts/` - Create blackout
- `GET /api/v1/blackouts/{blackout_id}` - Get blackout
- `PATCH /api/v1/blackouts/{blackout_id}` - Update blackout
- `DELETE /api/v1/blackouts/{blackout_id}` - Delete blackout

#### Slots
- `GET /api/v1/slots/` - Get available time slots

#### Bookings
- `GET /api/v1/bookings/` - List bookings
- `POST /api/v1/bookings/` - Create booking
- `GET /api/v1/bookings/{booking_id}` - Get booking
- `PATCH /api/v1/bookings/{booking_id}` - Update booking
- `DELETE /api/v1/bookings/{booking_id}` - Delete booking

### Testing Endpoints
Visit https://booking-beta.nbnesigns.co.uk/api/v1/docs for interactive API documentation.

---

## 🔄 Next Steps (Not Yet Implemented)

### LOOP 5: Email Notifications
- Configure SMTP settings (credentials already in .env)
- Test email sending for booking confirmations
- Set up email templates

### LOOP 6: Backups
- Set up automated PostgreSQL backups
- Configure backup retention policy
- Test restore procedure

### LOOP 7: Monitoring & Logging
- Set up uptime monitoring (e.g., UptimeRobot)
- Configure log rotation
- Add health check alerts
- Set up error tracking (e.g., Sentry)

### LOOP 8: Documentation & Validation
- Create API usage guide
- Document authentication flow
- Create troubleshooting runbook
- Perform load testing

### Frontend Development
- Choose framework (React/Next.js recommended)
- Design UI/UX
- Build booking interface
- Implement authentication
- Deploy frontend

---

## 📝 Important Notes

### Password Change History
- Original password: `!49Monkswood` (had issues with special character `!`)
- Changed to: `Monkswood49` (simpler, no special chars)
- This required updating both the Postgres container and the `.env` file

### CORS Configuration
- Initially had issues with Pydantic trying to parse CORS origins as JSON
- Fixed by modifying `api/core/config.py` to handle string input properly
- CORS must be uncommented in `.env` for the app to work with frontend

### Docker Compose File
- Using `docker-compose.vps.yml` for production
- Copied to `/srv/booking/docker/docker-compose.yml` on VPS
- Uses `env_file` directive to load `.env` file
- Connects to external `nbne-network` and `nbne-postgres` container

### SSL Certificates
- Automatically obtained and renewed by Caddy
- Stored in `/var/lib/caddy/`
- No manual intervention required

---

## 🔗 Useful Links

- **Live API:** https://booking-beta.nbnesigns.co.uk
- **API Docs:** https://booking-beta.nbnesigns.co.uk/api/v1/docs
- **GitHub Repo:** https://github.com/NBNEORIGIN/nbne-booking
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

**Last Updated:** February 2, 2026  
**Deployment Status:** ✅ Production Ready  
**Version:** 0.1.0-alpha
