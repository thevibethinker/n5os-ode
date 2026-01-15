---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_u0LhWqxkPWYn44Fg
---

# Service Fixes Build Plan

**Build ID:** service-fixes-2026-01-14
**Created:** 2026-01-14 23:35 ET
**Type:** Parallel Worker Build

## Context

Service cleanup revealed multiple broken/unhealthy services that need fixing. Issues clustered into 3 workers based on root cause similarity.

## Workers

### Worker 0: Prometheus 9p Filesystem Fix
**Scope:** Prometheus failing due to cross-device link error on 9p filesystem
**Root Cause:** Prometheus tries to rename blocks to `.tmp-for-deletion` which fails on 9p
**Fix Options:**
1. Configure Prometheus to use a different storage path (tmpfs at /dev/shm or similar)
2. Use --storage.tsdb.no-lockfile and manual cleanup
3. Accept Prometheus won't work reliably on this environment

**Decision:** TBD — may need to abandon telemetry cluster on Zo's architecture.

---

### Worker 1: N5 Import Path Fixes
**Scope:** Services failing due to `ModuleNotFoundError: No module named 'N5'`
**Root Cause:** Python import path not set correctly when running from service workdir
**Affected Services:**
- `slack-bot` (svc_0tUpbgAuKwY) — crashing on startup
- `crm-calendar-webhook` (svc_uvKvFPOTIGI) — likely same issue

**Fix Pattern:**
1. Add `PYTHONPATH=/home/workspace` to service env_vars, OR
2. Change workdir to `/home/workspace` and use absolute paths in entrypoint, OR
3. Refactor imports to use relative paths

**Files to check:**
- `/home/workspace/N5/services/slack_bot/receiver.py`
- `/home/workspace/N5/scripts/crm_calendar_webhook_handler.py`

---

### Worker 2: Webhook Receiver Health
**Scope:** Webhook services returning 404 (server running but no root handler)
**Root Cause:** Services designed for POST to specific endpoints, not GET /
**Affected Services:**
- `kondo-linkedin-webhook` — 404 on GET / (actually healthy, webhook endpoint works)
- `zapier-webhook` — 404 on GET / (actually healthy)  
- `fillout-webhook` — 404 on GET / (actually healthy)

**Status:** These are likely FALSE POSITIVES. The 404 is expected behavior.

**Verification needed:**
1. Check if POST endpoints work: `curl -X POST https://kondo-linkedin-webhook-va.zocomputer.io/webhook`
2. If POST works, these are healthy — no fix needed
3. Optionally add GET / health endpoint for monitoring

**Files:**
- `/home/workspace/N5/services/kondo-webhook/index.ts`
- `/home/workspace/webhook-receiver/server.js`
- `/home/workspace/Personal/Integrations/fillout/app.py`

---

### Worker 3: Poller/Monitor Crashes
**Scope:** Background pollers that have crashed
**Affected Services:**
- `fireflies-poller` (svc_koPo2TYE540) — 520 error
- `action-approvals-monitor` (svc_BNjB_ZJHGOY) — 520 error
- `task-completion-detector` (svc_IF7aNtRiL30) — 520 error

**Diagnosis:**
1. Check logs at `/dev/shm/<service>.log` and `_err.log`
2. Identify crash reason
3. Fix and restart

**Notes:**
- `fireflies-poller` may be redundant if webhook is working
- `action-approvals-monitor` and `task-completion-detector` are N5 task intelligence — check if still needed

---

## Deleted Services (this session)

| Service | Reason |
|---------|--------|
| n8n | User requested removal |
| zo-n8n-api | Depends on n8n |
| n5-metrics-collector | Telemetry dir missing |
| streaming-player-setup | Workdir missing |
| n5-bootstrap-support | Obsolete |
| n5-advisor | Obsolete |
| conversation-installer | Workdir missing |
| n5-conversation-api | Obsolete |
| zobridge-* (4 services) | Workdir missing |
| obsidian-web | Workdir missing |
| meeting-health-dashboard | Workdir missing |
| fabregas-cannon-staging | Workdir missing |
| travel-wrapped-2025 | Workdir missing |
| crm-webhook-renewal | Obsolete |
| crm-webhook-health | Obsolete |

## Remaining Healthy Services

~30 services remaining, all with valid workdirs and responding HTTP 200.

## Protocol Addition

Created `file 'N5/prefs/operations/service-cleanup-protocol.md'` for future maintenance.


