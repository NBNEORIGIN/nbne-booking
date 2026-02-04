# Production Deployment Guide

**NBNE Booking Platform**  
**Domain:** booking.nbnesigns.co.uk

---

## Prerequisites

- VPS with Docker and Docker Compose installed
- SSH access to the server
- Domain DNS access (Ionos)
- SMTP credentials for email

---

## Step 1: Configure DNS

**In your Ionos DNS settings:**

1. Go to your domain management for `nbnesigns.co.uk`
2. Add an **A Record**:
   - **Subdomain:** `booking`
   - **Points to:** Your VPS IP address
   - **TTL:** 3600 (1 hour)

3. Wait 5-15 minutes for DNS propagation

**Verify DNS:**
```bash
nslookup booking.nbnesigns.co.uk
# Should return your server IP
```

---

## Step 2: Prepare Server

**SSH to your server:**
```bash
ssh root@YOUR_SERVER_IP
```

**Create deployment directory:**
```bash
mkdir -p /srv/booking
mkdir -p /srv/backups
chmod 700 /srv/backups
```

---

## Step 3: Deploy Application

**Option A: Automated Deployment (Recommended)**

On your local machine:

1. **Edit deploy.sh** - Replace `YOUR_SERVER_IP` with your actual server IP

2. **Make executable:**
   ```bash
   chmod +x deploy.sh
   ```

3. **Run deployment:**
   ```bash
   ./deploy.sh
   ```

**Option B: Manual Deployment**

1. **Upload files to server:**
   ```bash
   scp -r api/ root@YOUR_SERVER_IP:/srv/booking/
   scp -r alembic/ root@YOUR_SERVER_IP:/srv/booking/
   scp -r scripts/ root@YOUR_SERVER_IP:/srv/booking/
   scp Dockerfile root@YOUR_SERVER_IP:/srv/booking/
   scp docker-compose.prod.yml root@YOUR_SERVER_IP:/srv/booking/docker-compose.yml
   scp Caddyfile root@YOUR_SERVER_IP:/srv/booking/
   scp alembic.ini root@YOUR_SERVER_IP:/srv/booking/
   ```

2. **SSH to server and continue with Step 4**

---

## Step 4: Configure Environment

**On the server:**

```bash
cd /srv/booking
nano .env
```

**Fill in these values:**

```env
# Database
POSTGRES_USER=booking_user
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE
POSTGRES_DB=booking_db

# Application
SECRET_KEY=YOUR_64_CHAR_RANDOM_STRING_HERE
PROJECT_NAME=NBNE Booking API
VERSION=1.0.0

# CORS
BACKEND_CORS_ORIGINS=["https://booking.nbnesigns.co.uk","https://nbnesigns.co.uk"]

# Email (use your Ionos SMTP)
SMTP_HOST=smtp.ionos.co.uk
SMTP_PORT=587
SMTP_USER=noreply@nbnesigns.co.uk
SMTP_PASSWORD=YOUR_EMAIL_PASSWORD
SMTP_FROM_EMAIL=noreply@nbnesigns.co.uk
SMTP_FROM_NAME=NBNE Booking

# Backup Settings
BACKUP_DIR=/srv/backups
BACKUP_RETENTION_DAYS=30
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

**Save and exit:** Ctrl+X, Y, Enter

---

## Step 5: Start Application

```bash
cd /srv/booking

# Build and start containers
docker compose up -d

# Wait for database to be ready
sleep 10

# Run migrations
docker compose exec api alembic upgrade head

# Check status
docker compose ps
```

**All containers should show "Up" status.**

---

## Step 6: Generate Backup Keys

```bash
cd /srv/booking
./scripts/generate_backup_keys.sh

# Copy the public key output
# Add to .env file:
nano .env
# Add: AGE_PUBLIC_KEY=age1...
# Add: AGE_SECRET_KEY=AGE-SECRET-KEY-1...

# Restart to apply
docker compose restart api
```

---

## Step 7: Set Up Automated Backups

```bash
# Test backup
./scripts/backup_database.sh

# Add to crontab for daily backups at 2 AM
crontab -e

# Add this line:
0 2 * * * /srv/booking/scripts/backup_database.sh

# Monthly cleanup (first day of month at 3 AM)
0 3 1 * * /srv/booking/scripts/cleanup_old_data.sh
```

---

## Step 8: Create Admin User

1. **Open browser:** https://booking.nbnesigns.co.uk/api/v1/docs

2. **Register admin user:**
   - Click `POST /api/v1/auth/register`
   - Click "Try it out"
   - Use this JSON:
   ```json
   {
     "email": "admin@nbnesigns.co.uk",
     "password": "YourSecurePassword123!",
     "full_name": "NBNE Admin",
     "role": "superadmin",
     "tenant_id": 1
   }
   ```
   - Click "Execute"

3. **Test login:**
   - Use `POST /api/v1/auth/login`
   - Get your JWT token

---

## Step 9: Create First Tenant

Using the admin token from login:

1. **Click "Authorize"** at top of Swagger UI
2. **Enter:** `Bearer YOUR_JWT_TOKEN`
3. **Click** `POST /api/v1/tenants`
4. **Create tenant:**
   ```json
   {
     "name": "Demo Client",
     "slug": "demo",
     "subdomain": "demo",
     "email": "demo@nbnesigns.co.uk",
     "phone": "+44 1234 567890",
     "client_display_name": "Demo Business",
     "primary_color": "#1a56db",
     "secondary_color": "#f3f4f6",
     "accent_color": "#10b981"
   }
   ```

---

## Verification Checklist

- [ ] DNS resolves to server IP
- [ ] HTTPS certificate issued (automatic via Caddy)
- [ ] Health check works: https://booking.nbnesigns.co.uk/health
- [ ] API docs accessible: https://booking.nbnesigns.co.uk/api/v1/docs
- [ ] Admin user created and can login
- [ ] First tenant created
- [ ] Backups configured and tested
- [ ] Email notifications working (test password reset)

---

## Monitoring

**Check logs:**
```bash
# Application logs
docker compose logs -f api

# Database logs
docker compose logs -f db

# Caddy logs
docker compose logs -f caddy

# All logs
docker compose logs -f
```

**Check container status:**
```bash
docker compose ps
```

**Check disk space:**
```bash
df -h
du -sh /srv/backups
```

---

## Maintenance

**Update application:**
```bash
cd /srv/booking
git pull  # if using git
docker compose build api
docker compose up -d
docker compose exec api alembic upgrade head
```

**Backup database manually:**
```bash
./scripts/backup_database.sh
```

**Restore from backup:**
```bash
./scripts/restore_database.sh /srv/backups/BACKUP_FILE.sql.age
```

**View audit logs:**
```bash
docker compose exec db psql -U booking_user -d booking_db -c "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 20;"
```

---

## Troubleshooting

**Container won't start:**
```bash
docker compose logs api
# Check for errors in .env file
```

**Database connection error:**
```bash
docker compose exec db psql -U booking_user -d booking_db
# If this fails, check POSTGRES_PASSWORD in .env
```

**SSL certificate not issued:**
```bash
docker compose logs caddy
# Check DNS is pointing to server
# Wait up to 10 minutes for Let's Encrypt
```

**Can't access API:**
```bash
# Check firewall
ufw status
ufw allow 80/tcp
ufw allow 443/tcp

# Check Caddy is running
docker compose ps caddy
```

---

## Security Notes

- ✅ All passwords hashed with Argon2id
- ✅ JWT tokens for authentication
- ✅ HTTPS enforced (automatic via Caddy)
- ✅ CSRF protection enabled
- ✅ Rate limiting active
- ✅ Security headers configured
- ✅ Audit logging enabled
- ✅ Backups encrypted
- ✅ GDPR compliant

---

## Support

For issues or questions:
- Check logs: `docker compose logs`
- Review documentation in `/docs` folder
- Check audit logs for security events

---

**Deployment complete! Your booking platform is live at https://booking.nbnesigns.co.uk** 🎉
