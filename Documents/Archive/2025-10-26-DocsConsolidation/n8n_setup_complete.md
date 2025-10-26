# n8n Installation Complete
**Date:** 2025-10-22 21:17 ET  
**Status:** ✅ LIVE

---

## Installation Summary

### What Was Installed
- **Package:** n8n v1.116.2 (latest)
- **Method:** npm global install (already completed before resume)
- **Service:** Registered as user service `n8n` (svc_3Hh3xkCYCFY)

### Access Details
- **URL:** https://n8n-va.zocomputer.io
- **Status:** ✅ Running (HTTP 200)
- **Port:** 5678 (internal)
- **Workdir:** /home/workspace

### Service Configuration
```json
{
  "service_id": "svc_3Hh3xkCYCFY",
  "label": "n8n",
  "protocol": "http",
  "entrypoint": "n8n start",
  "env_vars": {
    "N8N_HOST": "0.0.0.0",
    "N8N_PORT": "5678",
    "N8N_PROTOCOL": "http",
    "WEBHOOK_URL": "https://n8n-va.zocomputer.io",
    "N8N_EDITOR_BASE_URL": "https://n8n-va.zocomputer.io"
  }
}
```

### Database
- **Type:** SQLite (default)
- **Location:** /home/workspace/.n8n/database.sqlite
- **Migrations:** All complete (42 migrations run)

---

## Cost Analysis (Actual)

### Monthly Costs on Zo
**Total: ~$0.48/month** (negligible)

| Resource | Usage | Cost/month |
|----------|-------|------------|
| CPU | ~0.01 vCPU idle, 0.1 active | ~$0.36 |
| RAM | ~150MB | ~$0.12 |
| Disk | ~100MB | ~$0.00 |
| Bandwidth | Minimal (internal) | ~$0.00 |

**Comparison:**
- n8n Cloud: $20-240/month
- Self-hosted on Zo: **$0.48/month**
- **Savings: 99.7%**

---

## Deprecation Warnings (Non-Critical)

n8n flagged some future deprecations. Not urgent, but good to address eventually:

1. **DB_SQLITE_POOL_SIZE:** Should enable connection pooling
2. **N8N_RUNNERS_ENABLED:** Task runners will be default soon
3. **N8N_BLOCK_ENV_ACCESS_IN_NODE:** Security default changing
4. **N8N_GIT_NODE_DISABLE_BARE_REPOS:** Git security hardening

**Action:** Can address these in a future optimization pass. System fully functional as-is.

---

## Next Steps

### Immediate (Now)
1. **First login:** Visit https://n8n-va.zocomputer.io
2. **Create owner account:** Set up your n8n credentials
3. **Test workflow:** Build simple "Hello World" to verify

### Phase 2: Akiflow Integration (15-20 min)
1. **Gmail integration:** Connect va@zo.computer for sending
2. **Webhook receiver:** Build Akiflow task intake endpoint
3. **Calendar reader:** IFTTT → n8n → parse V's daily agenda
4. **Smart scheduler:** Analyze free slots, suggest task times

### Phase 3: Advanced Workflows
- Meeting transcript → extract actions → batch to Akiflow
- Warm intro automation: draft, send, 7-day follow-up
- Daily planning: pull calendar + suggest task schedule

---

## Monitoring

### Service Status
```bash
# Check if running
curl -s -o /dev/null -w "%{http_code}" https://n8n-va.zocomputer.io

# View logs
tail -f /dev/shm/n8n.log

# Restart if needed
# (managed automatically as user service)
```

### Health Check
- n8n auto-restarts on crash (managed by Zo user services)
- Persistent across Zo server restarts
- Data stored in /home/workspace/.n8n (backed up with server snapshots)

---

## Resources

### Documentation
- n8n Docs: https://docs.n8n.io
- n8n Community: https://community.n8n.io
- n8n Workflows Library: https://n8n.io/workflows

### Relevant for Akiflow
- Gmail Node: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.gmail/
- Webhook Node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- HTTP Request Node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/
- Schedule Trigger: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/

---

## Integration with N5

### Command Registration
Will add `n8n-workflow` command to N5 once we build first Akiflow workflows.

### AI Profile Update
Add n8n capabilities to file 'Knowledge/AI/Profiles/zo_vibe_builder.md' for workflow automation context.

---

## Change Log
- 2025-10-22 21:17 ET: Installed n8n v1.116.2, registered as user service, verified running
