# Security Baseline - NBNE Booking Platform

**Date:** February 3, 2026  
**Status:** LOOP 0 - Baseline Security Audit  
**Auditor:** WIGGUM Security Review

---

## 1. DATA INVENTORY

### 1.1 Personal Data Stored

**Tenant Table (`tenants`)**
- ❌ **No personal data** (business entity data only)
- Fields: name, email (business), phone (business), address (business)
- **GDPR Classification:** Business contact information (not personal data of individuals)

**Booking Table (`bookings`)**
- ✅ **PERSONAL DATA - HIGH RISK**
- `customer_name` - String(255) - **Personal identifier**
- `customer_email` - String(255) - **Personal identifier** (indexed)
- `customer_phone` - String(50) - **Personal identifier** (optional)
- `notes` - String(1000) - **May contain sensitive information**
- `start_time`, `end_time` - **Activity data**
- `status` - Booking status (confirmed/cancelled/completed/no_show)
- **Retention:** Indefinite (❌ RISK - no retention policy)
- **Tenant Isolation:** ✅ Has `tenant_id` foreign key

**Service Table (`services`)**
- ❌ **No personal data** (service catalog only)
- Fields: name, description, duration, price

**Availability Table (`availability`)**
- ❌ **No personal data** (schedule configuration only)

**Blackout Table (`blackouts`)**
- ❌ **No personal data** (schedule exceptions only)

### 1.2 Special Category Data (GDPR Article 9)

**Current Status:** ✅ **NONE IDENTIFIED**
- No health data
- No racial/ethnic data
- No political opinions
- No religious beliefs
- No biometric data
- No genetic data

**Risk:** ⚠️ `notes` field could inadvertently capture special category data
- **Mitigation Required:** User guidance + input validation

### 1.3 Credentials & Secrets

**Current Status:** ❌ **NO AUTHENTICATION SYSTEM**
- No user accounts
- No passwords
- No API keys stored in database
- No session management

**Environment Secrets (.env):**
- `POSTGRES_PASSWORD` - Database password
- `SMTP_PASSWORD` - Email service password
- `DATABASE_URL` - Contains embedded password

**Risk:** ⚠️ Secrets in environment variables (acceptable if managed correctly)

### 1.4 Files & Uploads

**Current Status:** ✅ **NO FILE STORAGE IMPLEMENTED**
- Logo URLs referenced (external)
- No file uploads
- No document storage

### 1.5 Logs

**Current Status:** ❌ **NO STRUCTURED LOGGING**
- Docker container logs (stdout/stderr)
- May contain request data including personal information
- No log retention policy
- No log sanitization

**Risk:** ⚠️ Personal data may leak into logs

---

## 2. TRUST BOUNDARIES

### 2.1 Network Architecture

```
Internet
    ↓
[Caddy Reverse Proxy] ← HTTPS (443)
    ↓ HTTP (internal)
[FastAPI App Container] ← Port 8000
    ↓ PostgreSQL protocol
[PostgreSQL Container] ← Port 5432
    ↓
[Docker Volume: postgres_data]
```

**Trust Boundaries:**
1. **Internet → Caddy:** Public, untrusted
2. **Caddy → App:** Internal Docker network (trusted)
3. **App → Database:** Internal Docker network (trusted)
4. **Database → Volume:** Host filesystem (trusted)

### 2.2 Application Layers

```
Browser (Untrusted)
    ↓ HTTPS
Public Routes (/public/*) ← No authentication
    ↓
Admin Routes (/admin/*) ← ❌ No authentication (CRITICAL)
    ↓
API Routes (/api/v1/*) ← ❌ No authentication (CRITICAL)
    ↓
Tenant Context Middleware ← Header-based (X-Tenant-Slug)
    ↓
Database Queries ← Filtered by tenant_id
    ↓
PostgreSQL
```

**Trust Boundaries:**
1. **Browser → Public Routes:** Untrusted input
2. **Public → Admin:** ❌ **NO BOUNDARY** (anyone can access admin)
3. **Admin → API:** ❌ **NO BOUNDARY** (anyone can call API)
4. **Middleware → Database:** Trusted (after tenant resolution)

### 2.3 Data Flow

**Booking Creation:**
```
Customer Form → POST /api/v1/bookings/
    ↓
Pydantic Validation (email, length)
    ↓
Tenant Context (from X-Tenant-Slug header)
    ↓
SQLAlchemy Insert (with tenant_id)
    ↓
PostgreSQL (bookings table)
```

**Admin Access:**
```
Browser → GET /admin/bookings
    ↓
❌ No authentication check
    ↓
Tenant from header (X-Tenant-Slug)
    ↓
Query bookings WHERE tenant_id = ?
    ↓
Render template with customer data
```

---

## 3. THREAT MODEL

### 3.1 Cross-Tenant Data Leakage

**Threat:** Tenant A accesses Tenant B's bookings

**Attack Vectors:**
1. ✅ **Mitigated:** Change `X-Tenant-Slug` header
   - Middleware resolves tenant from header
   - All queries filtered by `tenant_id`
   - **Status:** Appears secure (needs testing)

2. ❌ **VULNERABLE:** Guess booking IDs
   - Booking IDs are sequential integers
   - No tenant check in some endpoints?
   - **Risk:** HIGH if endpoints don't validate tenant ownership

3. ❌ **VULNERABLE:** SQL injection
   - No evidence of parameterized queries review
   - **Risk:** MEDIUM (SQLAlchemy should protect, but needs verification)

**Severity:** 🔴 **CRITICAL**  
**Likelihood:** 🟡 **MEDIUM** (requires header manipulation)

### 3.2 Staff Misuse

**Threat:** NBNE staff access client data without authorization

**Attack Vectors:**
1. ❌ **VULNERABLE:** No authentication
   - Anyone with URL can access admin panel
   - No audit trail of who accessed what
   - **Risk:** CRITICAL

2. ❌ **VULNERABLE:** No role-based access control
   - All staff have same access level
   - No principle of least privilege
   - **Risk:** HIGH

**Severity:** 🔴 **CRITICAL**  
**Likelihood:** 🔴 **HIGH** (no barriers)

### 3.3 Compromised Account

**Threat:** Attacker gains access to legitimate account

**Attack Vectors:**
1. ❌ **N/A:** No accounts exist yet
2. ⚠️ **FUTURE RISK:** Weak passwords, no MFA, session hijacking

**Severity:** 🟡 **HIGH** (when implemented)  
**Likelihood:** ⏸️ **N/A** (not implemented)

### 3.4 Injection Attacks

**Threat:** SQL injection, XSS, command injection

**Attack Vectors:**
1. **SQL Injection:**
   - ✅ **Likely Mitigated:** SQLAlchemy ORM (needs verification)
   - ⚠️ **Risk:** Raw SQL queries if any exist

2. **XSS (Cross-Site Scripting):**
   - ❌ **VULNERABLE:** Jinja2 templates auto-escape by default
   - ⚠️ **Risk:** `| safe` filter usage, user-controlled attributes
   - **Status:** Needs template audit

3. **Command Injection:**
   - ✅ **Not Applicable:** No system command execution

**Severity:** 🟡 **HIGH**  
**Likelihood:** 🟡 **MEDIUM**

### 3.5 File Exposure

**Threat:** Unauthorized access to uploaded files

**Attack Vectors:**
1. ✅ **Not Applicable:** No file uploads implemented

**Severity:** ⏸️ **N/A**  
**Likelihood:** ⏸️ **N/A**

### 3.6 Backup Exfiltration

**Threat:** Attacker accesses database backups

**Attack Vectors:**
1. ❌ **VULNERABLE:** No backup encryption
   - Backups likely stored as plain SQL dumps
   - **Risk:** CRITICAL

2. ❌ **VULNERABLE:** Backup location permissions
   - Unknown if backups are restricted
   - **Risk:** HIGH

**Severity:** 🔴 **CRITICAL**  
**Likelihood:** 🟡 **MEDIUM** (requires server access)

### 3.7 Misconfigured Caddy/Docker

**Threat:** Security misconfiguration exposes system

**Attack Vectors:**
1. ⚠️ **UNKNOWN:** Caddy security headers
   - HSTS status unknown
   - CSP status unknown
   - **Risk:** MEDIUM

2. ⚠️ **UNKNOWN:** Docker network isolation
   - Containers may be exposed to host network
   - **Risk:** MEDIUM

3. ✅ **LIKELY OK:** HTTPS enforcement
   - Caddy handles automatic HTTPS
   - **Status:** Needs verification

**Severity:** 🟡 **MEDIUM**  
**Likelihood:** 🟡 **MEDIUM**

---

## 4. CURRENT SECURITY POSTURE

### 4.1 What's Working

✅ **Tenant Isolation (Application Layer)**
- All tables have `tenant_id` foreign key
- Middleware enforces tenant context
- Queries filtered by tenant

✅ **Input Validation (Basic)**
- Pydantic schemas validate types
- Email format validation
- String length limits

✅ **HTTPS (Likely)**
- Caddy provides automatic HTTPS
- Certificate management automated

✅ **No Special Category Data**
- System doesn't collect sensitive health/biometric data

### 4.2 Critical Gaps

❌ **No Authentication System**
- Admin panel publicly accessible
- API endpoints unprotected
- No user accounts

❌ **No Authorization/RBAC**
- No roles (staff, admin, client)
- No permission checks
- No audit logging

❌ **No Rate Limiting**
- Brute force attacks possible
- API abuse possible
- No DDoS protection

❌ **No CSRF Protection**
- Forms vulnerable to CSRF
- State-changing requests unprotected

❌ **No Backup Encryption**
- Database backups unencrypted
- Backup access uncontrolled

❌ **No Audit Logging**
- No record of who accessed what
- No compliance trail
- No breach detection

❌ **No Data Retention Policy**
- Personal data stored indefinitely
- GDPR violation risk

❌ **No GDPR Processes**
- No data export (DSAR)
- No deletion workflow
- No breach response plan

---

## 5. RISK REGISTER

| # | Risk | Severity | Likelihood | Impact | Mitigation Loop |
|---|------|----------|------------|--------|-----------------|
| R1 | Unauthorized admin access | CRITICAL | HIGH | Data breach | LOOP 1 (Auth) |
| R2 | Cross-tenant data leakage | CRITICAL | MEDIUM | Data breach | LOOP 2 (RBAC) |
| R3 | No audit trail | HIGH | HIGH | Compliance failure | LOOP 5 (Audit) |
| R4 | Backup exfiltration | CRITICAL | MEDIUM | Data breach | LOOP 4 (Encryption) |
| R5 | CSRF attacks | HIGH | MEDIUM | Unauthorized actions | LOOP 3 (CSRF) |
| R6 | XSS attacks | HIGH | MEDIUM | Session hijacking | LOOP 3 (XSS) |
| R7 | No rate limiting | MEDIUM | HIGH | Service abuse | LOOP 3 (Rate limit) |
| R8 | Indefinite data retention | HIGH | HIGH | GDPR violation | LOOP 6 (Retention) |
| R9 | No DSAR capability | HIGH | HIGH | GDPR violation | LOOP 6 (DSAR) |
| R10 | Secrets in logs | MEDIUM | MEDIUM | Credential exposure | LOOP 4 (Secrets) |

---

## 6. SECURITY CONTROL PLAN

### LOOP 1: Authentication + Session Security
- [ ] Implement user model with password hashing (Argon2id)
- [ ] Add login/logout endpoints
- [ ] Secure session cookies (HttpOnly, Secure, SameSite)
- [ ] Rate limit login attempts
- [ ] Password reset flow with secure tokens
- [ ] Optional: MFA for staff/admin

### LOOP 2: RBAC + Tenant Isolation
- [ ] Define roles: SUPERADMIN, STAFF, CLIENT
- [ ] Implement permission decorators
- [ ] Add tenant ownership checks on all queries
- [ ] Consider PostgreSQL Row Level Security
- [ ] Write automated tenant isolation tests

### LOOP 3: Input Validation + Web Protections
- [ ] CSRF tokens for all forms
- [ ] Audit templates for XSS (| safe usage)
- [ ] Content Security Policy headers
- [ ] Rate limiting middleware
- [ ] Security headers (HSTS, X-Content-Type-Options, etc.)

### LOOP 4: Data Protection
- [ ] Secrets management (no hardcoding)
- [ ] Encrypted database backups (age/gpg)
- [ ] Test backup restore procedure
- [ ] Secure file storage (if implemented)
- [ ] Log sanitization

### LOOP 5: Audit Logging
- [ ] Audit log table (append-only)
- [ ] Log critical actions (login, data access, changes)
- [ ] Log retention policy
- [ ] No personal data in logs

### LOOP 6: GDPR Operational Readiness
- [ ] Data export (DSAR) endpoint
- [ ] Deletion/anonymization workflow
- [ ] Retention policy configuration
- [ ] Breach response runbook
- [ ] Privacy policy + terms

### LOOP 7: Validation + Evidence
- [ ] Automated security tests
- [ ] Penetration testing checklist
- [ ] Restore drill documentation
- [ ] Security documentation complete

---

## 7. EVIDENCE REQUIREMENTS

### Per-Loop Evidence

**LOOP 1:**
- [ ] Password hashing algorithm documented
- [ ] Rate limiting configuration
- [ ] Session security settings verified
- [ ] Password reset flow tested

**LOOP 2:**
- [ ] Tenant isolation tests passing
- [ ] RBAC permission matrix documented
- [ ] Cross-tenant access attempts blocked

**LOOP 3:**
- [ ] CSRF protection verified
- [ ] XSS payloads blocked
- [ ] Rate limits triggered and logged
- [ ] Security headers present

**LOOP 4:**
- [ ] Backup encryption verified
- [ ] Restore test successful
- [ ] Secrets not in code/logs
- [ ] Key rotation procedure documented

**LOOP 5:**
- [ ] Audit log schema documented
- [ ] Critical actions logged
- [ ] Log retention configured

**LOOP 6:**
- [ ] DSAR export tested
- [ ] Deletion workflow tested
- [ ] Retention policy configured
- [ ] Breach runbook documented

**LOOP 7:**
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Restore drill successful
- [ ] Exit checklist 100%

---

## 8. COMPLIANCE NOTES

### UK GDPR + DPA 2018

**Lawful Basis:**
- Likely: **Contract** (booking is contract performance)
- Possibly: **Legitimate Interest** (business operations)
- **Action:** Document lawful basis per data type

**Data Controller/Processor:**
- **NBNE:** Likely "Processor" for client's booking data
- **Client:** Likely "Controller" (determines purposes)
- **Action:** Data Processing Agreement required

**Individual Rights:**
- Right to access (DSAR) - ❌ Not implemented
- Right to rectification - ⚠️ Partial (can update bookings)
- Right to erasure - ❌ Not implemented
- Right to restrict processing - ❌ Not implemented
- Right to data portability - ❌ Not implemented

**Breach Notification:**
- 72-hour notification to ICO - ❌ No process
- Individual notification if high risk - ❌ No process

---

## 9. DEPLOYMENT ENVIRONMENT

**VPS Details:**
- IP: 87.106.65.142
- OS: Ubuntu 24.04
- Docker + Docker Compose
- Caddy reverse proxy
- PostgreSQL in container

**Network Exposure:**
- Port 443 (HTTPS) - Public
- Port 80 (HTTP) - Public (redirects to HTTPS)
- Port 8000 (App) - Internal only
- Port 5432 (PostgreSQL) - Internal only

**Volumes:**
- `postgres_data` - Database storage
- Unknown: Backup location
- Unknown: Log location

---

## 10. NEXT STEPS

### Immediate Actions (LOOP 1)
1. Implement authentication system
2. Protect admin routes
3. Add rate limiting to login

### Short-term (LOOPS 2-3)
1. Implement RBAC
2. Add CSRF protection
3. Security headers via Caddy

### Medium-term (LOOPS 4-6)
1. Encrypted backups
2. Audit logging
3. GDPR workflows

### Before Production
1. All 7 loops complete
2. Exit checklist 100%
3. Penetration test
4. Legal review (DPA, privacy policy)

---

## STATUS: LOOP 0 COMPLETE ✅

**Findings:**
- ✅ Data inventory complete
- ✅ Trust boundaries mapped
- ✅ Threat model documented
- ✅ Risk register created
- ✅ Control plan defined
- ✅ Evidence requirements specified

**Critical Risks Identified:** 10  
**Mitigation Loops Required:** 7  
**Estimated Effort:** 20-30 hours

**Next:** LOOP 1 - Authentication + Session Security
