# Release Checklist

## Pre-Release

### Code Quality
- [ ] All Wiggum loops completed and marked PASS
- [ ] No TODO/FIXME comments in critical paths
- [ ] Code reviewed (if team available)
- [ ] All tests passing locally
- [ ] No secrets in codebase (check with git grep)

### Configuration
- [ ] Environment variables documented in infra/.env.example
- [ ] Production environment variables set in hosting platform
- [ ] Database connection string configured
- [ ] Email service credentials configured
- [ ] SMS service credentials configured (if enabled)
- [ ] Feature flags set appropriately

### Database
- [ ] Migrations tested locally
- [ ] Migrations run on staging/production
- [ ] Backup procedure tested
- [ ] Restore procedure tested and documented

### Security
- [ ] Rate limiting enabled
- [ ] Honeypot fields in place
- [ ] Input validation comprehensive
- [ ] HTTPS enforced
- [ ] CORS configured appropriately
- [ ] Admin authentication working

## Deployment

### Build & Deploy
- [ ] Build succeeds without errors
- [ ] Deploy to hosting platform (Render/Vercel/Netlify)
- [ ] Health endpoint accessible
- [ ] Database migrations applied
- [ ] Static assets loading correctly

### Smoke Tests (Post-Deploy)
Run these tests immediately after deployment:

1. **Health Check**
   - [ ] GET /health returns 200 OK
   - [ ] Response includes database status

2. **Tenant Resolution**
   - [ ] Access via subdomain resolves correctly
   - [ ] Tenant context loaded properly

3. **Admin Access**
   - [ ] Admin login page loads
   - [ ] Admin can log in
   - [ ] Admin dashboard loads

4. **Services**
   - [ ] Admin can view services list
   - [ ] Admin can create a service
   - [ ] Admin can edit a service
   - [ ] Admin can delete a service

5. **Availability**
   - [ ] Admin can view availability
   - [ ] Admin can set availability windows
   - [ ] Admin can create blackouts

6. **Slot Generation**
   - [ ] Slots API returns available times
   - [ ] Slots respect availability windows
   - [ ] Slots respect blackouts

7. **Booking Creation**
   - [ ] Customer can view available slots
   - [ ] Customer can create a booking
   - [ ] Booking appears in admin
   - [ ] Double-booking is prevented

8. **Notifications**
   - [ ] Email sent to customer on booking
   - [ ] Email sent to business on booking
   - [ ] SMS sent (if feature enabled)

9. **CSV Export**
   - [ ] Admin can export bookings to CSV
   - [ ] CSV contains correct data

10. **Multi-Tenant Isolation**
    - [ ] Tenant A cannot see Tenant B's data
    - [ ] Tenant A cannot book Tenant B's services

## Post-Release Monitoring

### First 24 Hours
- [ ] Monitor error logs
- [ ] Check health endpoint periodically
- [ ] Verify backups running
- [ ] Monitor email delivery
- [ ] Check for any 500 errors

### First Week
- [ ] Review booking patterns
- [ ] Check for any double-bookings
- [ ] Verify notification delivery rates
- [ ] Review performance metrics
- [ ] Gather pilot client feedback

## Rollback Procedure

If critical issues arise:

1. **Immediate Actions**
   - [ ] Notify pilot clients
   - [ ] Document the issue
   - [ ] Assess severity

2. **Rollback Steps**
   - [ ] Revert to previous deployment via hosting platform
   - [ ] Verify health endpoint
   - [ ] Run smoke tests on rolled-back version
   - [ ] Restore database if needed (from backup)

3. **Database Rollback** (if migrations were applied)
   - [ ] Stop application
   - [ ] Restore database from pre-deployment backup
   - [ ] Verify data integrity
   - [ ] Restart application on previous version

4. **Post-Rollback**
   - [ ] Confirm system stability
   - [ ] Notify pilot clients of resolution
   - [ ] Document root cause
   - [ ] Plan fix and re-deployment

## Pilot Client Onboarding

For each new pilot client:

1. **Tenant Setup**
   - [ ] Create tenant record in database
   - [ ] Configure subdomain/slug
   - [ ] Set tenant-specific settings

2. **Initial Configuration**
   - [ ] Admin user created
   - [ ] Services configured
   - [ ] Availability windows set
   - [ ] Test booking created and verified

3. **Training**
   - [ ] Admin walkthrough completed
   - [ ] Documentation provided
   - [ ] Support contact shared

4. **Go-Live**
   - [ ] Embed booking widget/link on client site
   - [ ] Verify end-to-end flow
   - [ ] Monitor first few bookings
