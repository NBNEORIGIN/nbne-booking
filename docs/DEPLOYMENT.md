# Deployment Guide

## Overview
This guide covers deploying the NBNE Booking system to production.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (managed or self-hosted)
- SMTP credentials for email notifications
- Domain name configured
- SSL/TLS certificate

## Environment Configuration

### Required Environment Variables

```bash
# Database
POSTGRES_SERVER=your-db-host
POSTGRES_USER=booking_user
POSTGRES_PASSWORD=strong-password-here
POSTGRES_DB=booking_db
POSTGRES_PORT=5432

# API
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Your Business Name

# Feature Flags
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=false
```

## Deployment Options

### Option 1: Render.com (Recommended for MVP)

1. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - Create new PostgreSQL database
   - Note connection details

2. **Create Web Service**
   - Connect GitHub repository
   - Select Docker deployment
   - Set environment variables
   - Deploy

3. **Configure Custom Domain**
   - Add custom domain in Render
   - Update DNS records
   - Enable automatic SSL

### Option 2: AWS ECS/Fargate

1. **Build and push Docker image**
   ```bash
   docker build -t booking-api .
   docker tag booking-api:latest your-ecr-repo/booking-api:latest
   docker push your-ecr-repo/booking-api:latest
   ```

2. **Create RDS PostgreSQL instance**
3. **Create ECS task definition**
4. **Create ECS service**
5. **Configure Application Load Balancer**
6. **Set up Route53 for DNS**

### Option 3: DigitalOcean App Platform

1. **Create PostgreSQL cluster**
2. **Create App from GitHub**
3. **Configure environment variables**
4. **Deploy**

### Option 4: Self-Hosted VPS

1. **Provision server** (Ubuntu 22.04 LTS recommended)
2. **Install Docker and Docker Compose**
3. **Clone repository**
4. **Configure environment variables**
5. **Set up Nginx reverse proxy**
6. **Configure SSL with Let's Encrypt**
7. **Start services**

## Post-Deployment Steps

### 1. Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

### 2. Create Initial Tenant

```bash
docker-compose exec api python scripts/seed_tenants.py
```

Or via API:
```bash
curl -X POST "https://yourdomain.com/api/v1/tenants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Business",
    "slug": "your-business",
    "subdomain": "yourbusiness",
    "email": "contact@yourbusiness.com",
    "phone": "+1-555-1234"
  }'
```

### 3. Verify Health Endpoint

```bash
curl https://yourdomain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "NBNE Booking API",
  "version": "0.1.0-alpha"
}
```

### 4. Test Email Notifications

Create a test booking and verify emails are sent.

### 5. Configure Monitoring

Set up monitoring for:
- Application health
- Database connections
- Error rates
- Response times
- Disk usage

## DNS Configuration

### For Subdomain-Based Tenancy

```
*.yourdomain.com    A    your-server-ip
yourdomain.com      A    your-server-ip
```

Or with CNAME:
```
*.yourdomain.com    CNAME    your-app.onrender.com
```

## SSL/TLS Configuration

### Using Let's Encrypt (Self-Hosted)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d *.yourdomain.com
```

### Using Cloud Provider

Most cloud providers (Render, AWS, DigitalOcean) provide automatic SSL.

## Nginx Configuration (Self-Hosted)

```nginx
server {
    listen 80;
    server_name yourdomain.com *.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com *.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Scaling Considerations

### Horizontal Scaling
- Run multiple API containers behind load balancer
- Use managed PostgreSQL with read replicas
- Implement Redis for session/cache if needed

### Vertical Scaling
- Increase container resources (CPU/memory)
- Upgrade database instance size
- Optimize database queries

## Monitoring and Logging

### Application Logs
```bash
docker-compose logs -f api
```

### Database Logs
Check your database provider's logging interface.

### Error Tracking
Consider integrating:
- Sentry for error tracking
- DataDog for APM
- CloudWatch (AWS)
- Render logs (Render.com)

## Backup Configuration

See `BACKUP_STRATEGY.md` for detailed backup procedures.

**Quick setup:**
1. Enable automated backups on database
2. Set retention period (30 days minimum)
3. Test restore procedure
4. Document recovery steps

## Security Checklist

See `SECURITY.md` for comprehensive security guide.

**Essential items:**
- [ ] HTTPS enabled
- [ ] Strong database password
- [ ] SMTP credentials secured
- [ ] CORS configured correctly
- [ ] Environment variables not in code
- [ ] Database not publicly accessible
- [ ] Regular security updates

## Troubleshooting

### Application won't start
- Check environment variables
- Verify database connection
- Check Docker logs

### Database connection errors
- Verify database is running
- Check connection string
- Verify firewall rules

### Emails not sending
- Verify SMTP credentials
- Check SMTP port not blocked
- Test with telnet/openssl

### Admin UI not loading
- Verify Jinja2 installed
- Check template directory exists
- Verify admin routes registered

## Rollback Procedure

1. **Identify last working version**
2. **Pull previous Docker image**
   ```bash
   docker pull your-repo/booking-api:previous-tag
   ```
3. **Stop current containers**
   ```bash
   docker-compose down
   ```
4. **Update docker-compose.yml to use previous image**
5. **Start containers**
   ```bash
   docker-compose up -d
   ```
6. **Verify functionality**

## Performance Optimization

### Database
- Add indexes on frequently queried columns
- Enable connection pooling
- Use read replicas for reporting

### Application
- Enable response caching where appropriate
- Optimize database queries
- Use async endpoints for I/O operations

### Infrastructure
- Use CDN for static assets
- Enable gzip compression
- Use HTTP/2

## Cost Optimization

### Render.com (Estimated)
- PostgreSQL: $7-25/month
- Web Service: $7-25/month
- **Total: ~$15-50/month**

### AWS (Estimated)
- RDS PostgreSQL: $15-100/month
- ECS Fargate: $15-50/month
- Load Balancer: $16/month
- **Total: ~$50-170/month**

### DigitalOcean (Estimated)
- Managed PostgreSQL: $15-50/month
- App Platform: $12-24/month
- **Total: ~$30-75/month**

## Support

For deployment issues:
- Check documentation in `/docs`
- Review logs for errors
- Verify environment configuration
- Test locally with Docker Compose

## Next Steps After Deployment

1. Monitor application for 24-48 hours
2. Set up automated backups
3. Configure monitoring alerts
4. Document any custom configuration
5. Train team on admin interface
6. Set up staging environment
7. Plan for future enhancements
