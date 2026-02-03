# Data Breach Response Plan

**NBNE Booking Platform**  
**Last Updated:** February 3, 2026  
**Owner:** Security Team

---

## Overview

This document outlines the procedures to follow in the event of a suspected or confirmed data breach affecting the NBNE Booking Platform.

**Legal Requirement:** Under UK GDPR and DPA 2018, data breaches must be reported to the ICO within 72 hours if they pose a risk to individuals' rights and freedoms.

---

## 1. Detection & Initial Response

### Breach Indicators

**System Indicators:**
- Unusual database queries in logs
- Unexpected data exports
- Failed authentication attempts from unusual locations
- Unauthorized access to admin panel
- Unusual API activity patterns
- Rate limit violations
- Security event spikes in audit logs

**External Indicators:**
- Reports from users about unauthorized access
- Suspicious emails sent from the system
- Data appearing on dark web/paste sites
- Third-party security notifications

### Immediate Actions (Within 1 Hour)

1. **Contain the Breach**
   - Isolate affected systems
   - Disable compromised accounts
   - Block suspicious IP addresses
   - Revoke compromised API keys/tokens
   - Take affected services offline if necessary

2. **Preserve Evidence**
   - Snapshot affected systems
   - Export audit logs
   - Capture network traffic logs
   - Document all actions taken
   - Do NOT delete or modify evidence

3. **Assemble Response Team**
   - Technical Lead
   - Security Officer
   - Legal Counsel
   - Communications Lead
   - Data Protection Officer (if applicable)

---

## 2. Assessment (Within 4 Hours)

### Determine Scope

**Questions to Answer:**
- What data was accessed/exfiltrated?
- How many individuals affected?
- What type of data (personal, sensitive, financial)?
- When did the breach occur?
- How did the breach occur?
- Is the breach ongoing?
- What systems are affected?

**Data Classification:**
- **Personal Data:** Names, emails, phone numbers
- **Sensitive Data:** Passwords (hashed), authentication tokens
- **Business Data:** Tenant information, booking details
- **System Data:** Audit logs, configuration

### Risk Assessment

**High Risk Indicators:**
- Passwords compromised (even if hashed)
- Financial data accessed
- Large number of individuals affected (>100)
- Sensitive personal data exposed
- Data publicly disclosed
- Ongoing unauthorized access

**Medium Risk Indicators:**
- Contact information only
- Limited number of individuals (<100)
- Data not publicly disclosed
- Breach contained quickly

**Low Risk Indicators:**
- No personal data accessed
- System data only
- No evidence of exfiltration
- Attempted breach prevented

---

## 3. Notification Requirements

### ICO Notification (Within 72 Hours)

**Required if:**
- Breach likely to result in risk to individuals' rights and freedoms
- Personal data compromised
- Unable to rule out risk

**Not Required if:**
- No personal data involved
- Data encrypted and key not compromised
- Risk mitigated before harm occurs
- Unlikely to result in risk

**How to Report:**
- Online: https://ico.org.uk/for-organisations/report-a-breach/
- Phone: 0303 123 1113
- Email: casework@ico.org.uk

**Information to Provide:**
- Nature of breach
- Categories and approximate number of individuals affected
- Categories and approximate number of records affected
- Contact details of DPO or contact point
- Likely consequences
- Measures taken or proposed

### Individual Notification

**Required if:**
- High risk to individuals' rights and freedoms
- Sensitive data compromised
- Financial harm possible
- Identity theft risk

**Timeline:**
- Without undue delay
- As soon as reasonably possible
- May be delayed if law enforcement requests

**Communication Method:**
- Email (primary)
- In-app notification
- Website notice
- Postal mail (if email unavailable)

**Message Content:**
- What happened (in plain language)
- What data was affected
- What we're doing about it
- What individuals should do
- Contact information for questions
- Apology and reassurance

---

## 4. Containment & Remediation

### Immediate Containment

```bash
# Disable compromised user accounts
docker exec booking-db psql -U nbne_admin -d nbne_main -c \
  "UPDATE users SET is_active = false WHERE id IN (1,2,3);"

# Revoke all JWT tokens (rotate secret key)
# Edit .env and restart application
export SECRET_KEY="new-secret-key-here"
docker compose restart app

# Block suspicious IP addresses (via Caddy/firewall)
# Add to Caddyfile:
# @blocked {
#   remote_ip 1.2.3.4 5.6.7.8
# }
# respond @blocked 403

# Take system offline if necessary
docker compose down
```

### Investigation

1. **Review Audit Logs**
   ```sql
   -- Find suspicious activity
   SELECT * FROM audit_logs
   WHERE timestamp > '2026-02-01'
   AND (action = 'unauthorized_access' OR success = 'failure')
   ORDER BY timestamp DESC;
   
   -- Find data exports
   SELECT * FROM audit_logs
   WHERE action IN ('data_export', 'booking_export')
   AND timestamp > '2026-02-01';
   ```

2. **Check System Logs**
   ```bash
   # Application logs
   docker logs booking-app --since 24h | grep -i "error\|unauthorized\|failed"
   
   # Database logs
   docker logs booking-db --since 24h | grep -i "error\|failed"
   
   # Web server logs
   docker logs caddy --since 24h | grep -i "403\|401\|500"
   ```

3. **Analyze Attack Vector**
   - SQL injection attempt?
   - Compromised credentials?
   - API vulnerability?
   - Social engineering?
   - Insider threat?
   - Third-party compromise?

### Remediation

1. **Patch Vulnerabilities**
   - Apply security updates
   - Fix identified vulnerabilities
   - Update dependencies
   - Strengthen access controls

2. **Reset Credentials**
   - Force password reset for affected users
   - Rotate API keys
   - Rotate database passwords
   - Rotate backup encryption keys

3. **Enhance Monitoring**
   - Add alerts for suspicious activity
   - Increase audit logging
   - Implement additional security controls

---

## 5. Recovery

### System Restoration

1. **Verify Security**
   - Confirm vulnerabilities patched
   - Verify no backdoors remain
   - Check for additional compromises
   - Run security scans

2. **Restore Services**
   - Bring systems back online gradually
   - Monitor for anomalies
   - Verify functionality
   - Communicate status to users

3. **Post-Incident Monitoring**
   - Enhanced monitoring for 30 days
   - Daily security reviews
   - Weekly status updates

---

## 6. Post-Incident Review

### Within 1 Week

**Conduct Review Meeting:**
- What happened?
- How did it happen?
- What worked well?
- What didn't work?
- What can be improved?

**Document Lessons Learned:**
- Root cause analysis
- Timeline of events
- Actions taken
- Effectiveness of response
- Recommendations

**Update Procedures:**
- Revise this plan based on learnings
- Update security controls
- Improve monitoring
- Enhance training

### Report to Management

**Executive Summary:**
- What happened
- Impact assessment
- Actions taken
- Cost (if applicable)
- Recommendations
- Preventive measures

---

## 7. Contact Information

### Internal Contacts

**Technical Lead:**
- Name: [To be filled]
- Email: tech@nbnesigns.co.uk
- Phone: [To be filled]

**Security Officer:**
- Name: [To be filled]
- Email: security@nbnesigns.co.uk
- Phone: [To be filled]

**Legal Counsel:**
- Name: [To be filled]
- Email: legal@nbnesigns.co.uk
- Phone: [To be filled]

### External Contacts

**ICO (Information Commissioner's Office):**
- Website: https://ico.org.uk
- Phone: 0303 123 1113
- Email: casework@ico.org.uk

**Action Fraud (Cybercrime):**
- Website: https://www.actionfraud.police.uk
- Phone: 0300 123 2040

**NCSC (National Cyber Security Centre):**
- Website: https://www.ncsc.gov.uk
- Email: report@phishing.gov.uk

---

## 8. Templates

### ICO Breach Notification Template

```
Subject: Data Breach Notification - NBNE Booking Platform

Date of Breach: [Date]
Date Discovered: [Date]
Organization: NBNE Signs Ltd
Contact: [Name, Email, Phone]

1. Nature of Breach:
[Description of what happened]

2. Data Affected:
- Categories: [e.g., names, emails, phone numbers]
- Number of individuals: [Approximate number]
- Number of records: [Approximate number]

3. Likely Consequences:
[Potential impact on individuals]

4. Measures Taken:
[Actions taken to address the breach]

5. Measures Proposed:
[Actions to prevent future breaches]

Additional Information:
[Any other relevant details]
```

### User Notification Template

```
Subject: Important Security Notice - NBNE Booking

Dear [Name],

We are writing to inform you of a security incident that may have affected your personal information.

What Happened:
On [date], we discovered [brief description of breach].

What Information Was Involved:
The following information may have been accessed:
- [List of data types]

What We're Doing:
We have taken the following steps:
- [List of actions]

What You Should Do:
We recommend that you:
- Change your password immediately
- Monitor your accounts for suspicious activity
- [Other recommendations]

We sincerely apologize for this incident and any concern it may cause.

For Questions:
If you have any questions, please contact us at:
Email: security@nbnesigns.co.uk
Phone: [Phone number]

Sincerely,
NBNE Signs Ltd
```

---

## 9. Prevention Checklist

**Regular Activities:**
- [ ] Weekly security log reviews
- [ ] Monthly vulnerability scans
- [ ] Quarterly penetration testing
- [ ] Annual security audit
- [ ] Continuous monitoring of audit logs
- [ ] Regular backup testing
- [ ] Security awareness training
- [ ] Incident response drills

**Technical Controls:**
- [ ] Multi-factor authentication
- [ ] Encryption at rest and in transit
- [ ] Regular security updates
- [ ] Access control reviews
- [ ] Network segmentation
- [ ] Intrusion detection
- [ ] Rate limiting
- [ ] Input validation

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-03 | Security Team | Initial version |

---

**This document should be reviewed and updated annually or after any security incident.**
