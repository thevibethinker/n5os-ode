# Scheduled Task Instruction: Daily N5 Health Check

**Title:** 📊 Daily N5 Health Check  
**RRULE:** `FREQ=DAILY;BYHOUR=8;BYMINUTE=0` (8:00 AM ET daily)  
**Model:** gpt-5-mini (routine monitoring)  
**Delivery:** email

---

## Purpose

Run daily N5 system health check and email summary report to V with recommendations for stale files, empty files, uncommitted changes, and pending tasks.

---

## Prerequisites

- file 'N5/telemetry/n5_health_check.py' exists and is executable
- file 'N5/telemetry/daily_report.md' can be written
- Email delivery configured for user

---

## Execution

1. **Run Health Check Script**
   ```bash
   python3 /home/workspace/N5/telemetry/n5_health_check.py
   ```
   
   This will:
   - Count stale files in Records/Temporary/ (>7 days)
   - Find empty files in N5/scripts, Knowledge/, Documents/System
   - Check for uncommitted git changes
   - Scan Lists/ for pending tasks
   - Generate daily_report.md with recommendations

2. **Verify Report Generated**
   - Check that file 'N5/telemetry/daily_report.md' exists
   - Confirm it contains current timestamp (today's date)
   - If missing, log error and abort (don't send empty email)

3. **Send Email Digest**
   - Read contents of file 'N5/telemetry/daily_report.md'
   - Use `send_email_to_user` tool with:
     - Subject: "N5 Daily Health Check"
     - Body: Full contents of daily_report.md (markdown format)

---

## Success Criteria

- ✅ Health check script executed without errors (exit code 0)
- ✅ file 'N5/telemetry/daily_report.md' created with today's timestamp
- ✅ file 'N5/telemetry/health_history.jsonl' appended with new entry
- ✅ Email delivered to user with readable markdown report

---

## Error Handling

**If health check script fails:**
- Log error message from script stderr
- Send email with error summary: "N5 health check failed to run. Check logs at N5/telemetry/"
- Do not attempt to send non-existent report

**If report file missing:**
- Log error: "Health check completed but report file not found"
- Send email: "N5 health check completed but report generation failed"
- Include raw health_history.jsonl last line as fallback

**If email send fails:**
- Log error (email tool will handle retry)
- Append failure note to N5/telemetry/email_failures.log for review

---

## Monitoring

**Key Metrics:**
- Daily execution success rate (target: >95%)
- Average stale files count (alert if >20)
- Empty files count (alert if >10)
- Email delivery confirmation

**Weekly Review:**
- Check health_history.jsonl for trends
- Identify recurring stale file patterns
- Validate recommendations are actionable

---

## References

- file 'N5/telemetry/n5_health_check.py' — Health check implementation
- file 'N5/telemetry/README.md' — Telemetry system overview
- file 'N5/prefs/operations/scheduled-task-protocol.md' — Task creation standards

---

## Notes

- **Purpose:** Daily system health monitoring with email digest
- **Dependencies:** Python 3.12, git, send_email_to_user tool
- **Output:** N5/telemetry/daily_report.md, health_history.jsonl
- **Monitor:** Email delivery, report generation success
- **Owner:** System-managed, V reviews recommendations
- **Cost:** Minimal (mini model, <1min execution)

---

*v1.0 | Created 2025-10-26 | Phase 1 telemetry implementation*
