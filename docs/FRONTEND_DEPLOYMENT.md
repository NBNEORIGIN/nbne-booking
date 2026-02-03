# Frontend Deployment Guide - NBNE Booking

## Prerequisites

- VPS with Docker and Docker Compose
- Git repository access
- Domain with SSL configured (Caddy)
- Database migrations applied

## Deployment Steps

### 1. Pull Latest Code

```bash
cd /srv/booking/app
git pull origin main
```

### 2. Rebuild Containers

```bash
cd /srv/booking/docker
docker compose down
docker compose up -d --build
```

### 3. Apply Migrations (if needed)

```bash
docker exec booking-app alembic upgrade head
```

### 4. Verify Deployment

```bash
# Check container status
docker compose ps

# Check logs
docker logs booking-app --tail 50

# Test health endpoint
curl https://booking-beta.nbnesigns.co.uk/health
```

### 5. Test Frontend

```bash
# Test public preview (requires tenant)
curl -H "X-Tenant-Slug: your-tenant" https://booking-beta.nbnesigns.co.uk/public/preview

# Test booking page
curl -H "X-Tenant-Slug: your-tenant" https://booking-beta.nbnesigns.co.uk/public/book
```

## Creating Test Data

### Option 1: Via Script

```bash
# On VPS
cd /srv/booking/app
bash scripts/setup_vps_preview.sh
```

### Option 2: Via API

```bash
# Create tenant
curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/tenants/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "demo",
    "name": "Demo Company",
    "email": "demo@example.com",
    "phone": "+44 20 1234 5678",
    "primary_color": "#FF5722"
  }'

# Create service
curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/services/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: demo" \
  -d '{
    "name": "Consultation",
    "duration_minutes": 30,
    "price": 50.00,
    "is_active": true
  }'

# Create availability
curl -X POST https://booking-beta.nbnesigns.co.uk/api/v1/availability/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: demo" \
  -d '{
    "day_of_week": 1,
    "start_time": "09:00:00",
    "end_time": "17:00:00"
  }'
```

## Accessing the Frontend

### Public Booking Pages

**With Browser Extension (ModHeader):**
1. Install ModHeader extension
2. Add header: `X-Tenant-Slug: your-tenant-slug`
3. Visit: `https://booking-beta.nbnesigns.co.uk/public/book`

**With Subdomain (if configured):**
- Visit: `https://your-tenant.booking-beta.nbnesigns.co.uk/public/book`

### Admin Pages

**Branding Settings:**
- URL: `https://booking-beta.nbnesigns.co.uk/admin/branding`
- Add header: `X-Tenant-Slug: your-tenant-slug`

**Bookings Management:**
- URL: `https://booking-beta.nbnesigns.co.uk/admin/bookings`
- Add header: `X-Tenant-Slug: your-tenant-slug`

## Troubleshooting

### Frontend Not Loading

**Check container logs:**
```bash
docker logs booking-app --tail 100
```

**Common issues:**
- Migrations not applied: Run `alembic upgrade head`
- Template files not found: Rebuild container with `--build`
- Tenant not found: Check tenant exists and is active

### Branding Not Showing

**Verify tenant has branding:**
```bash
curl https://booking-beta.nbnesigns.co.uk/api/v1/tenants/your-tenant-slug
```

**Check branding fields are set:**
- `primary_color` should be hex format
- `client_display_name` should be set
- Tenant should be active

### Styles Not Loading

**Check Tailwind CDN:**
- Verify internet connection from server
- Check browser console for CDN errors
- Tailwind CDN: `https://cdn.tailwindcss.com`

### 404 Errors

**Verify routes are registered:**
```bash
# Check main.py includes public router
docker exec booking-app grep "public_router" /app/api/main.py
```

**Check URL paths:**
- Public routes: `/public/*`
- Admin routes: `/admin/*`
- API routes: `/api/v1/*`

## Performance Optimization

### Current Setup
- Tailwind CSS via CDN (no build step)
- Minimal JavaScript
- Server-rendered templates
- No image optimization (logo only)

### Future Improvements
- Add Tailwind build step for production
- Implement CDN for static assets
- Add image optimization
- Enable gzip compression in Caddy
- Add browser caching headers

## Monitoring

### Health Check
```bash
curl https://booking-beta.nbnesigns.co.uk/health
```

### Application Logs
```bash
docker logs booking-app -f
```

### Database Logs
```bash
docker logs booking-db -f
```

## Rollback Procedure

If deployment fails:

```bash
# 1. Check previous commit
git log --oneline -5

# 2. Rollback to previous version
git checkout <previous-commit-hash>

# 3. Rebuild
docker compose down
docker compose up -d --build

# 4. Verify
curl https://booking-beta.nbnesigns.co.uk/health
```

## Security Checklist

- [x] HTTPS enabled (Caddy)
- [x] Environment variables secured
- [x] Database credentials in .env
- [x] No secrets in code
- [x] CORS configured
- [x] Tenant isolation enforced
- [ ] Rate limiting (future)
- [ ] Authentication (future)

## Backup

### Database Backup
```bash
docker exec booking-db pg_dump -U nbne_admin nbne_main > backup_$(date +%Y%m%d).sql
```

### Code Backup
```bash
# Code is in Git repository
git push origin main
```

## Support

For deployment issues:
- Check logs: `docker logs booking-app`
- Review documentation: `/docs`
- Contact: support@nbnesigns.co.uk
