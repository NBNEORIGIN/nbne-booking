# Backup and Disaster Recovery Strategy

## Overview
Backup strategy and disaster recovery procedures for the NBNE Booking system.

## Backup Requirements

### Recovery Objectives
- **RPO (Recovery Point Objective):** 1 hour - Maximum acceptable data loss
- **RTO (Recovery Time Objective):** 4 hours - Maximum acceptable downtime

## Backup Strategy

### 1. Database Backups

**Daily Automated Backups**
- Frequency: Daily at 2:00 AM UTC
- Retention: 30 days
- Location: Cloud storage (S3/equivalent) + local

**Continuous WAL Archiving (Production)**
- Enable PostgreSQL Write-Ahead Logging
- Point-in-time recovery capability
- 7-day retention

### 2. Application Backups

**Code Repository**
- Git version control (continuous)
- Indefinite retention

**Docker Images**
- Registry: Docker Hub/ECR
- Last 10 versions retained

### 3. Backup Schedule

| Type | Frequency | Retention | Location |
|------|-----------|-----------|----------|
| DB Full | Daily 2AM | 30 days | S3 + Local |
| DB WAL | Continuous | 7 days | S3 |
| DB Weekly | Sunday 2AM | 90 days | S3 Glacier |
| Code | Continuous | Indefinite | Git |
| Images | On build | 10 versions | Registry |

## Disaster Recovery Procedures

### Scenario 1: Database Corruption
1. Stop application
2. Identify last good backup
3. Restore database from backup
4. Run migrations
5. Verify data integrity
6. Restart application

**Expected Duration:** 2-3 hours

### Scenario 2: Complete Server Failure
1. Provision new server
2. Install dependencies
3. Clone repository
4. Download latest backup
5. Restore database
6. Update DNS
7. Verify functionality

**Expected Duration:** 3-4 hours

### Scenario 3: Accidental Data Deletion
1. Create database snapshot
2. Restore to temporary database
3. Extract affected data
4. Import to production
5. Verify with user

**Expected Duration:** 1-2 hours

## Backup Monitoring

### Alerts
- Backup failure
- Backup duration >30 minutes
- Storage >80% full
- Missing daily backup

### Verification
- Weekly automated restore tests
- Monthly manual restore to staging
- Quarterly full disaster recovery drill

## Security

- Encrypt backups at rest (AES-256)
- Encrypt backups in transit (TLS)
- Limit access to authorized personnel
- Audit backup access logs

## Compliance

- Booking data: 7 years retention
- Audit logs: 1 year minimum
- GDPR: Include backups in data deletion process

## Backup Checklist

**Daily:**
- Verify automated backup completed
- Check backup file size
- Verify cloud upload

**Weekly:**
- Run backup verification script
- Review backup logs

**Monthly:**
- Restore test to staging
- Review procedures

**Quarterly:**
- Full disaster recovery drill
- Update documentation
