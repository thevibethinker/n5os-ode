---
task: Kondo LinkedIn Webhook Debug
type: debug
priority: high
parent_build: zo-task-system (separate but related)
---

# Kondo LinkedIn Webhook Debug

## Problem
Kondo webhook last synced LinkedIn messages on **Jan 22**. Should be syncing continuously. 471 messages in DB but nothing recent.

## Investigation Steps

1. **Check webhook service status**:
   ```bash
   curl -I https://kondo-linkedin-webhook-va.zocomputer.io/health 2>/dev/null || echo "No health endpoint"
   ```

2. **Check webhook logs**:
   ```bash
   tail -100 /dev/shm/kondo-linkedin-webhook.log 2>/dev/null
   tail -100 /dev/shm/kondo-linkedin-webhook_err.log 2>/dev/null
   ```

3. **Check if service is registered and running**:
   ```bash
   # List services
   # Check port 8765
   lsof -i :8765
   ```

4. **Check Kondo dashboard** — is the webhook still configured? Has the auth token expired?
   - Kondo dashboard: https://app.trykondo.com
   - V may need to re-auth or update webhook URL

5. **Check webhook event log in DB**:
   ```sql
   sqlite3 /home/workspace/Knowledge/linkedin/linkedin.db "SELECT * FROM webhook_events ORDER BY rowid DESC LIMIT 10;"
   ```

6. **Test webhook manually** — can we trigger a test payload?

## Likely Issues
- Webhook URL changed or service not running
- Kondo auth token expired
- Kondo stopped sending (their side)
- Service crashed and didn't restart

## Deliverable
- Identify root cause
- Fix the sync
- Verify new messages coming through
- Report back to orchestrator conversation: `con_OaZwIOzCydglh4r4`

When done, text V: "Kondo fixed. [X] new messages synced."
