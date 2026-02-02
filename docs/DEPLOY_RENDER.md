# Render Deployment Guide - NBNE Booking Beta

**Environment:** Beta  
**Domain:** booking-beta.nbnesigns.co.uk  
**Purpose:** 1-3 pilot clients before VPS migration

---

## Prerequisites

- GitHub repository with code pushed
- Render account (https://render.com)
- Access to DNS management for nbnesigns.co.uk
- SMTP credentials (Gmail with app password recommended)

---

## Deployment Steps

### 1. Create Render Account & Connect GitHub

1. Go to https://render.com and sign up
2. Connect your GitHub account
3. Authorize Render to access your repository

### 2. Deploy Using render.yaml (Recommended)

**Option A: Blueprint Deploy (Easiest)**

1. Go to Render Dashboard
2. Click "New" → "Blueprint"
3. Connect your repository
4. Select the repository containing `render.yaml`
5. Render will automatically detect and create:
   - PostgreSQL database: `nbne-booking-db-beta`
   - Web service: `nbne-booking-api-beta`
6. Click "Apply" to deploy

**Option B: Manual Service Creation**

If blueprint doesn't work, create services manually:

#### Create PostgreSQL Database

1. Dashboard → "New" → "PostgreSQL"
2. Settings:
   - **Name:** `nbne-booking-db-beta`
   - **Database:** `booking_db`
   - **User:** `booking_user`
   - **Region:** Frankfurt (or closest to users)
   - **Plan:** Starter ($7/month)
3. Click "Create Database"
4. **Save the Internal Database URL** (starts with `postgresql://`)

#### Create Web Service

1. Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Settings:
   - **Name:** `nbne-booking-api-beta`
   - **Region:** Frankfurt (same as database)
   - **Branch:** `main` (or your default branch)
   - **Root Directory:** `.` (leave empty)
   - **Environment:** Docker
   - **Plan:** Starter ($7/month)
   - **Dockerfile Path:** `./Dockerfile`
   - **Docker Context:** `.`
   - **Health Check Path:** `/health`
4. Click "Create Web Service"

### 3. Configure Environment Variables

In the web service settings, add these environment variables:

**Required:**
```
DATABASE_URL=<from-database-internal-url>
BACKEND_CORS_ORIGINS=https://booking-beta.nbnesigns.co.uk,https://nbne-booking-api-beta.onrender.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=noreply@nbnesigns.co.uk
FROM_NAME=NBNE Booking
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=false
```

**How to get DATABASE_URL:**
- Go to your PostgreSQL database in Render
- Copy the "Internal Database URL" (NOT External)
- Paste as DATABASE_URL value

**SMTP Setup (Gmail):**
1. Enable 2FA on your Google account
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate app password for "Mail"
4. Use this 16-character password as SMTP_PASSWORD

### 4. Run Database Migrations

After first deployment:

1. Go to web service → "Shell" tab
2. Run:
   ```bash
   alembic upgrade head
   ```
3. Verify migrations completed successfully

**Alternative: Add as Build Command**
In web service settings:
- **Build Command:** `pip install -r api/requirements.txt && alembic upgrade head`
- **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### 5. Seed Initial Data (Optional)

In the Shell tab:
```bash
python scripts/seed_tenants.py
```

This creates 3 test tenants:
- acme-corp
- beauty-salon
- tech-consulting

---

## DNS Configuration

### Configure booking-beta.nbnesigns.co.uk

**Step 1: Get Render URL**
1. Go to your web service in Render
2. Find the default URL (e.g., `nbne-booking-api-beta.onrender.com`)

**Step 2: Add Custom Domain in Render**
1. Web service → Settings → Custom Domains
2. Click "Add Custom Domain"
3. Enter: `booking-beta.nbnesigns.co.uk`
4. Render will show DNS instructions

**Step 3: Configure DNS**

Go to your DNS provider (Cloudflare, Route53, etc.) and add:

**Option A: CNAME (Recommended)**
```
Type: CNAME
Name: booking-beta
Value: nbne-booking-api-beta.onrender.com
TTL: Auto or 300
Proxy: Disabled (if using Cloudflare)
```

**Option B: A Record (if CNAME not supported)**
Render will provide IP addresses - add as A records.

**Step 4: SSL Certificate**
- Render automatically provisions SSL via Let's Encrypt
- Wait 5-15 minutes for certificate issuance
- Verify HTTPS works: https://booking-beta.nbnesigns.co.uk/health

---

## Backup Strategy

### Automated Backups (Render)

Render PostgreSQL includes:
- **Daily snapshots** (retained for 7 days on Starter plan)
- **Point-in-time recovery** available

**Access backups:**
1. Database → Backups tab
2. View available snapshots
3. Restore to new database if needed

### Manual Backup Procedure

**Export database:**
```bash
# From Render Shell or local with external URL
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

**Download via Render:**
1. Database → Connect → External Database URL
2. Use `pg_dump` locally:
   ```bash
   pg_dump "postgresql://user:pass@host/db" > backup.sql
   ```

**Restore from backup:**
```bash
psql $DATABASE_URL < backup.sql
```

### Backup Schedule Recommendation

- **Daily:** Automated by Render
- **Weekly:** Manual export and store in secure location (S3, Google Drive)
- **Before major changes:** Manual snapshot

---

## Rollback Procedure

### Rollback to Previous Deployment

1. Go to web service → Deploys tab
2. Find the last working deployment
3. Click "..." → "Redeploy"
4. Confirm rollback

**OR via Git:**
1. Identify last working commit: `git log`
2. Revert: `git revert <commit-hash>`
3. Push: `git push`
4. Render auto-deploys

### Rollback Database Migration

If migration fails:
```bash
# In Render Shell
alembic downgrade -1  # Go back one migration
# or
alembic downgrade <revision>  # Go to specific revision
```

**Emergency: Restore from Backup**
1. Database → Backups
2. Select snapshot
3. Restore to new database
4. Update DATABASE_URL in web service
5. Restart web service

---

## Monitoring & Health Checks

### Health Endpoint

**URL:** https://booking-beta.nbnesigns.co.uk/health

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "NBNE Booking API",
  "version": "0.1.0-alpha"
}
```

### Render Monitoring

**Built-in metrics:**
- CPU usage
- Memory usage
- Response times
- Error rates

**Access:** Web service → Metrics tab

### Set Up Alerts

1. Web service → Settings → Notifications
2. Add email for:
   - Deploy failures
   - Service crashes
   - High error rates

### Log Access

**View logs:**
- Web service → Logs tab
- Real-time streaming
- Filter by severity

**Download logs:**
```bash
# Via Render CLI
render logs -s nbne-booking-api-beta
```

---

## Smoke Test Checklist

Run these tests after deployment:

### 1. Service Health
- [ ] Health endpoint responds: `curl https://booking-beta.nbnesigns.co.uk/health`
- [ ] Returns `{"status":"healthy"}`
- [ ] Response time < 1 second

### 2. API Documentation
- [ ] Swagger UI loads: https://booking-beta.nbnesigns.co.uk/docs
- [ ] All endpoints visible
- [ ] Can expand and view schemas

### 3. Admin UI Access
- [ ] Admin UI loads: https://booking-beta.nbnesigns.co.uk/admin/bookings
- [ ] Add header: `X-Tenant-Slug: acme-corp` (use ModHeader extension)
- [ ] Bookings page displays
- [ ] Navigation tabs work (Bookings, Services, Availability)

### 4. Tenant Isolation
- [ ] List tenants: `curl https://booking-beta.nbnesigns.co.uk/api/v1/tenants/`
- [ ] Returns array of tenants
- [ ] Each tenant has: name, slug, email

### 5. Services CRUD
```bash
# Create service
curl -X POST "https://booking-beta.nbnesigns.co.uk/api/v1/services/" \
  -H "X-Tenant-Slug: acme-corp" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Service","duration_minutes":60}'

# List services
curl -H "X-Tenant-Slug: acme-corp" \
  "https://booking-beta.nbnesigns.co.uk/api/v1/services/"
```
- [ ] Service created successfully
- [ ] Service appears in list
- [ ] Service visible in admin UI

### 6. Availability Configuration
```bash
# Create availability
curl -X POST "https://booking-beta.nbnesigns.co.uk/api/v1/availability/" \
  -H "X-Tenant-Slug: acme-corp" \
  -H "Content-Type: application/json" \
  -d '{"day_of_week":1,"start_time":"09:00","end_time":"17:00"}'
```
- [ ] Availability created
- [ ] Visible in admin UI → Availability tab

### 7. Slot Generation
```bash
curl "https://booking-beta.nbnesigns.co.uk/api/v1/slots/?service_id=1&start_date=2026-02-10&end_date=2026-02-14" \
  -H "X-Tenant-Slug: acme-corp"
```
- [ ] Returns array of available slots
- [ ] Slots respect availability rules
- [ ] Slots are correct duration

### 8. Booking Creation
```bash
curl -X POST "https://booking-beta.nbnesigns.co.uk/api/v1/bookings/" \
  -H "X-Tenant-Slug: acme-corp" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id":1,
    "start_time":"2026-02-10T10:00:00",
    "end_time":"2026-02-10T11:00:00",
    "customer_name":"Test Customer",
    "customer_email":"test@example.com",
    "customer_phone":"+1-555-1234"
  }'
```
- [ ] Booking created (201 status)
- [ ] Booking appears in admin UI
- [ ] Email sent to customer (if SMTP configured)
- [ ] Email sent to business (if SMTP configured)

### 9. CSV Export
- [ ] Admin UI → Bookings → Export CSV button
- [ ] CSV downloads successfully
- [ ] CSV contains booking data
- [ ] Filename includes tenant slug and timestamp

### 10. Double-Booking Prevention
```bash
# Try to create overlapping booking
curl -X POST "https://booking-beta.nbnesigns.co.uk/api/v1/bookings/" \
  -H "X-Tenant-Slug: acme-corp" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id":1,
    "start_time":"2026-02-10T10:30:00",
    "end_time":"2026-02-10T11:30:00",
    "customer_name":"Another Customer",
    "customer_email":"another@example.com"
  }'
```
- [ ] Returns 409 Conflict error
- [ ] Error message indicates time slot unavailable
- [ ] Original booking unchanged

### 11. Database Persistence
- [ ] Create booking
- [ ] Restart web service (Render → Manual Deploy → Restart)
- [ ] Verify booking still exists
- [ ] Data persisted correctly

### 12. Error Handling
- [ ] Try invalid tenant: `curl -H "X-Tenant-Slug: invalid" https://booking-beta.nbnesigns.co.uk/admin/bookings`
- [ ] Returns 404 with proper error message
- [ ] Try invalid booking time: past date
- [ ] Returns 400 with validation error

---

## Troubleshooting

### Service Won't Start

**Check logs:**
1. Web service → Logs tab
2. Look for errors in startup

**Common issues:**
- Missing environment variables
- Database connection failed
- Port binding issues

**Fix:**
- Verify all required env vars set
- Check DATABASE_URL is internal URL
- Ensure PORT is not hardcoded

### Database Connection Errors

**Symptoms:**
- "could not connect to server"
- "connection refused"

**Solutions:**
1. Verify DATABASE_URL uses **internal** URL (not external)
2. Check database is running (Database → Status)
3. Verify database and web service in same region
4. Check IP allowlist (should be empty for internal connections)

### Migrations Fail

**Error:** "relation already exists" or "column does not exist"

**Solutions:**
1. Check current migration state:
   ```bash
   alembic current
   ```
2. If out of sync, stamp current version:
   ```bash
   alembic stamp head
   ```
3. Re-run migrations:
   ```bash
   alembic upgrade head
   ```

### Admin UI Shows "Tenant not found"

**Cause:** Missing `X-Tenant-Slug` header

**Solutions:**
1. Install ModHeader browser extension
2. Add header: `X-Tenant-Slug: acme-corp`
3. Refresh page

**Alternative:** Use curl with header for testing

### Emails Not Sending

**Check:**
1. SMTP credentials correct
2. SMTP_HOST and SMTP_PORT set
3. FROM_EMAIL set
4. ENABLE_EMAIL_NOTIFICATIONS=true

**Gmail specific:**
- Must use App Password (not regular password)
- 2FA must be enabled
- Check "Less secure apps" not blocking

**Test:**
```bash
# In Render Shell
python -c "
from api.services.email_service import email_service
result = email_service.send_booking_confirmation_to_customer(
    customer_email='test@example.com',
    customer_name='Test',
    service_name='Test Service',
    start_time=datetime.now(),
    end_time=datetime.now(),
    tenant_name='Test Tenant',
    tenant_email='tenant@example.com'
)
print('Email sent:', result)
"
```

### High Response Times

**Check:**
1. Database query performance
2. Number of concurrent requests
3. Plan resources (upgrade if needed)

**Optimize:**
- Add database indexes (already included)
- Enable connection pooling (already configured)
- Consider upgrading plan

### SSL Certificate Issues

**Symptoms:**
- "Not secure" warning
- Certificate errors

**Solutions:**
1. Wait 15 minutes after adding custom domain
2. Verify DNS propagation: `dig booking-beta.nbnesigns.co.uk`
3. Check Render → Custom Domains → Certificate status
4. If stuck, remove and re-add custom domain

---

## Cost Estimate

**Render Pricing (as of 2026):**
- PostgreSQL Starter: $7/month
- Web Service Starter: $7/month
- **Total: ~$14/month**

**Included:**
- 512MB RAM (web service)
- 1GB RAM (database)
- Daily backups (7-day retention)
- SSL certificate
- 100GB bandwidth

**Upgrade paths:**
- Standard plan: $25/month (more resources)
- Pro plan: $85/month (dedicated resources)

---

## Security Checklist

Before going live:

- [ ] SMTP credentials stored as environment variables (not in code)
- [ ] DATABASE_URL not committed to git
- [ ] CORS origins restricted to production domain
- [ ] SSL certificate active and valid
- [ ] Database not publicly accessible (internal URL only)
- [ ] Health endpoint does not expose sensitive data
- [ ] Error messages don't leak system information
- [ ] Backup procedure tested and documented
- [ ] Monitoring alerts configured
- [ ] Admin routes documented (auth to be added later)

---

## Next Steps After Deployment

1. **Test with pilot clients:**
   - Create tenant for each client
   - Configure their services and availability
   - Train on admin UI usage

2. **Monitor for 1-2 weeks:**
   - Check error rates
   - Monitor response times
   - Verify email delivery
   - Check backup completion

3. **Gather feedback:**
   - UI/UX improvements needed
   - Feature requests
   - Performance issues

4. **Plan VPS migration:**
   - Only after proven traction
   - Document migration path
   - Plan zero-downtime cutover

---

## Support & Resources

**Render Documentation:**
- https://render.com/docs
- https://render.com/docs/databases
- https://render.com/docs/deploy-fastapi

**Project Documentation:**
- `docs/SECURITY.md` - Security hardening
- `docs/BACKUP_STRATEGY.md` - Detailed backup procedures
- `docs/EMAIL_SETUP.md` - Email configuration
- `docs/DEPLOYMENT.md` - General deployment guide

**Emergency Contacts:**
- Render Support: https://render.com/support
- Database issues: Check Render status page

---

## Deployment Checklist

Use this before each deployment:

**Pre-Deployment:**
- [ ] All tests passing locally: `docker-compose exec api pytest`
- [ ] Code committed and pushed to GitHub
- [ ] Environment variables documented
- [ ] Migration scripts tested locally
- [ ] Backup of production database taken

**Deployment:**
- [ ] Deploy via Render (auto or manual)
- [ ] Monitor deployment logs
- [ ] Run migrations if needed
- [ ] Verify health endpoint
- [ ] Run smoke tests

**Post-Deployment:**
- [ ] Verify all smoke tests pass
- [ ] Check error logs for issues
- [ ] Test critical user flows
- [ ] Notify pilot clients if needed
- [ ] Document any issues encountered

---

**Last Updated:** 2026-02-02  
**Environment:** Beta  
**Status:** Ready for deployment
