# Security Hardening Guide

## Overview
This document outlines security measures implemented in the NBNE Booking system and recommendations for production deployment.

## Implemented Security Measures

### 1. Multi-Tenant Isolation
**Status:** ✅ Implemented

- All database queries filtered by `tenant_id`
- Tenant resolution via subdomain, header, or path
- Middleware enforces tenant context
- Tests verify tenant isolation

**Risk Mitigation:**
- Prevents cross-tenant data access
- Ensures data privacy between customers

### 2. Database Security
**Status:** ✅ Implemented

- Connection pooling with `pool_pre_ping=True`
- Parameterized queries (SQLAlchemy ORM)
- No raw SQL execution
- Transaction isolation for booking creation

**Risk Mitigation:**
- Prevents SQL injection
- Ensures data consistency
- Handles connection failures gracefully

### 3. Input Validation
**Status:** ✅ Implemented

- Pydantic models validate all inputs
- Email validation via `email-validator`
- Date/time validation
- Enum validation for status fields

**Risk Mitigation:**
- Prevents invalid data entry
- Ensures data integrity
- Protects against malformed requests

### 4. CORS Configuration
**Status:** ✅ Implemented

- Configurable via `BACKEND_CORS_ORIGINS`
- Restricts cross-origin requests
- Environment-specific settings

**Risk Mitigation:**
- Prevents unauthorized cross-origin access
- Protects against CSRF attacks

### 5. Error Handling
**Status:** ✅ Implemented

- Generic error messages to clients
- Detailed logging server-side
- No stack traces in production responses
- Graceful failure for email notifications

**Risk Mitigation:**
- Prevents information disclosure
- Maintains system stability

## Production Security Checklist

### Environment Variables
- [ ] Change all default passwords
- [ ] Use strong database passwords (16+ chars, mixed case, numbers, symbols)
- [ ] Generate secure `SECRET_KEY` for JWT/sessions
- [ ] Use app-specific passwords for SMTP (not main account password)
- [ ] Store secrets in secure vault (AWS Secrets Manager, HashiCorp Vault)
- [ ] Never commit `.env` file to version control

### Database Security
- [ ] Enable SSL/TLS for database connections
- [ ] Use read-only database user for reporting queries
- [ ] Enable database audit logging
- [ ] Regular database backups (see BACKUP_STRATEGY.md)
- [ ] Encrypt database backups
- [ ] Restrict database network access (VPC/firewall)

### API Security
- [ ] Enable HTTPS only (redirect HTTP to HTTPS)
- [ ] Use valid SSL/TLS certificates (Let's Encrypt, AWS ACM)
- [ ] Implement rate limiting (see Rate Limiting section)
- [ ] Add authentication for admin routes
- [ ] Implement API key authentication for programmatic access
- [ ] Enable request logging
- [ ] Set security headers (see Headers section)

### Network Security
- [ ] Use firewall rules to restrict access
- [ ] Only expose necessary ports (443 for HTTPS)
- [ ] Use VPC/private subnets for database
- [ ] Enable DDoS protection (Cloudflare, AWS Shield)
- [ ] Monitor for suspicious traffic patterns

### Application Security
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Run security scans (`safety check`, `bandit`)
- [ ] Enable container scanning (Snyk, Trivy)
- [ ] Use non-root user in Docker container
- [ ] Minimize Docker image size (fewer attack vectors)

## Recommended Additions for Production

### 1. Rate Limiting
**Priority:** HIGH

```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@router.post("/bookings/")
@limiter.limit("10/minute")
def create_booking(...):
    ...
```

**Recommended Limits:**
- Booking creation: 10/minute per IP
- API reads: 100/minute per IP
- Admin routes: 50/minute per IP

### 2. Authentication for Admin Routes
**Priority:** HIGH

```python
# Basic HTTP Auth for MVP
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Apply to admin routes
@router.get("/admin/bookings")
def admin_bookings(admin: str = Depends(verify_admin), ...):
    ...
```

### 3. Security Headers
**Priority:** MEDIUM

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com", "*.yourdomain.com"])
```

### 4. Audit Logging
**Priority:** MEDIUM

```python
# Log all booking operations
import logging

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

def log_booking_created(booking, tenant, user_ip):
    audit_logger.info(
        f"BOOKING_CREATED tenant={tenant.slug} booking_id={booking.id} "
        f"customer={booking.customer_email} ip={user_ip}"
    )
```

### 5. Input Sanitization
**Priority:** LOW (Pydantic handles most cases)

```python
import bleach

def sanitize_text(text: str) -> str:
    """Remove HTML/script tags from user input."""
    return bleach.clean(text, tags=[], strip=True)
```

## Security Monitoring

### Metrics to Track
- Failed authentication attempts
- Rate limit violations
- Database connection errors
- Unusual booking patterns (rapid creation, cancellation)
- API error rates
- Response time anomalies

### Alerting
Set up alerts for:
- Multiple failed auth attempts from same IP
- Sudden spike in traffic
- Database connection failures
- High error rates (>5% of requests)
- Disk space low (<20%)

### Log Retention
- Application logs: 30 days
- Audit logs: 1 year
- Access logs: 90 days
- Error logs: 90 days

## Incident Response Plan

### 1. Detection
- Monitor alerts and logs
- Customer reports
- Automated security scans

### 2. Assessment
- Determine severity (Critical, High, Medium, Low)
- Identify affected systems/data
- Estimate impact

### 3. Containment
- Isolate affected systems
- Block malicious IPs
- Disable compromised accounts
- Take database snapshot

### 4. Eradication
- Remove malicious code/access
- Patch vulnerabilities
- Reset compromised credentials
- Update firewall rules

### 5. Recovery
- Restore from clean backup if needed
- Verify system integrity
- Monitor for recurrence
- Gradual service restoration

### 6. Post-Incident
- Document incident details
- Update security measures
- Notify affected parties if required
- Conduct lessons learned review

## Compliance Considerations

### GDPR (if serving EU customers)
- [ ] Implement data export functionality
- [ ] Implement data deletion (right to be forgotten)
- [ ] Add privacy policy
- [ ] Add cookie consent
- [ ] Maintain data processing records
- [ ] Implement breach notification process

### PCI DSS (if handling payments)
- [ ] Never store credit card data
- [ ] Use PCI-compliant payment processor
- [ ] Encrypt payment data in transit
- [ ] Regular security audits

### HIPAA (if handling health data)
- [ ] Encrypt data at rest and in transit
- [ ] Implement access controls
- [ ] Maintain audit logs
- [ ] Business associate agreements
- [ ] Regular risk assessments

## Security Testing

### Pre-Production
- [ ] Run `safety check` for vulnerable dependencies
- [ ] Run `bandit` for Python security issues
- [ ] Test authentication bypass attempts
- [ ] Test SQL injection (should be prevented by ORM)
- [ ] Test XSS attacks (should be prevented by Pydantic)
- [ ] Test CSRF attacks (should be prevented by CORS)
- [ ] Test rate limiting
- [ ] Test tenant isolation

### Ongoing
- [ ] Monthly dependency updates
- [ ] Quarterly security reviews
- [ ] Annual penetration testing
- [ ] Continuous vulnerability scanning

## Contact Information

**Security Issues:**
Report security vulnerabilities to: security@yourdomain.com

**Response Time:**
- Critical: 4 hours
- High: 24 hours
- Medium: 1 week
- Low: 1 month

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
