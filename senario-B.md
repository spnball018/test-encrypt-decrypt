# Scenario B: Data Leak Incident Response

## Scenario
A developer accidentally logged **Decrypted National ID** into Cloud Logging for 24 hours.

---

## Immediate Actions

1. **Lock Down Logs**
   - Restrict log system access to security team only.
   - Review and remove unnecessary IAM permissions.

2. **Stop the Leak**
   - Disable or roll back the affected service.
   - Fix the code and redeploy.

3. **Preserve Evidence**
   - Take an encrypted backup of logs for investigation.
   - Keep access strictly limited.

4. **Remove Sensitive Logs**
   - Delete or redact sensitive log entries.
   - Clean logs from exports and backups if possible.

5. **Notify Stakeholders**
   - Inform security, legal, and management.
   - Check if regulatory reporting is required.

---

## Remediation

- Check who accessed the logs.
- Identify root cause.
- Patch code to prevent sensitive data logging.
- Add test to ensure decrypted data is never logged.

---

## Prevention Controls
1. **Team Learning**
   - Run blameless postmortem.
   - Share lessons and update guidelines.
2. **Automatic Masking**
   - Mask PII fields in logs by default.

3. **Safe Logging Library**
   - Use shared logger that blocks sensitive fields.

4. **CI/CD Rules**
   - Add linter/security scan to detect sensitive logging.

5. **Code Review Checklist**
   - Require PII logging check in PR reviews.
