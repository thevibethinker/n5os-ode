---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_u0LhWqxkPWYn44Fg
status: complete
---

# Worker 1: N5 Import Path Fixes

## Objective

Fix services crashing due to `ModuleNotFoundError: No module named 'N5'`

## Affected Services

1. **slack-bot** (svc_0tUpbgAuKwY)
   - Entrypoint: `python3 /home/workspace/N5/services/slack_bot/receiver.py`
   - Workdir: `/home/workspace`
   - Error: `from N5.lib import paths` fails

2. **crm-calendar-webhook** (svc_uvKvFPOTIGI)
   - Entrypoint: `python3 /home/workspace/N5/scripts/crm_calendar_webhook_handler.py`
   - Error: Likely same import issue

## Root Cause

When Python runs a script, it adds the script's directory to `sys.path`, not the parent. So `N5.lib` imports fail because `/home/workspace` isn't in the path.

## Fix Options

### Option A: Add PYTHONPATH env var (preferred)
```bash
# Update service with:
env_vars: {"PYTHONPATH": "/home/workspace"}
```

### Option B: Wrapper script with cd
```bash
entrypoint: "bash -c 'cd /home/workspace && python3 -m N5.services.slack_bot.receiver'"
```

### Option C: Refactor imports (most work)
Change `from N5.lib import X` to relative imports.

## Tasks

1. [x] Check slack-bot error logs: `tail /dev/shm/slack-bot_err.log`
2. [x] Update slack-bot service with PYTHONPATH
3. [x] Test slack-bot responds
4. [x] Check crm-calendar-webhook logs
5. [x] Update crm-calendar-webhook service (not needed - already working)
6. [x] Test crm-calendar-webhook responds

## Verification

```bash
curl -s -o /dev/null -w "%{http_code}" https://slack-bot-va.zocomputer.io/
curl -s -o /dev/null -w "%{http_code}" https://crm-calendar-webhook-va.zocomputer.io/
```

Both should return 200 or appropriate webhook response.


