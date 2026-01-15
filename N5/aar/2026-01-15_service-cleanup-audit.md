---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_u0LhWqxkPWYn44Fg
---

# AAR: Service Cleanup & Maintenance Protocol

**Date:** 2026-01-15  
**Type:** Infrastructure maintenance  
**Duration:** ~45 minutes  
**Outcome:** ✅ Success

## Executive Summary

Comprehensive audit and cleanup of Zo user services. Reduced service count from 46 to ~30 by removing broken and obsolete services. Created formal service cleanup protocol for future maintenance. Discovered architectural limitation with Prometheus on 9p filesystem.

## What We Set Out To Do

1. Review all registered user services
2. Identify and remove outdated/broken services
3. Define a cleanup protocol for future service purging
4. Fix remaining service issues

## What Actually Happened

### Phase 1: Audit
- Listed all 46 services via `list_user_services`
- Categorized by: broken (missing workdir), obsolete, potentially obsolete, healthy

### Phase 2: Cleanup
- **Deleted 18 services:**
  - 10 with missing workdirs (streaming-player-setup, zobridge-*, obsidian-web, etc.)
  - 6 obsolete (n8n, n5-bootstrap-support, n5-advisor, crm-webhook-renewal, etc.)
  - 2 additional (zo-n8n-api, n5-metrics-collector)

### Phase 3: Fixes
- Reactivated `did-i-get-it` with correct entrypoint
- Wiped Prometheus stale data to clear 9p filesystem error
- Verified remaining services healthy

### Phase 4: Protocol Creation
- Created `N5/prefs/operations/service-cleanup-protocol.md`
- Updated `N5/config/PORT_REGISTRY.md`

## Key Findings

### 9p Filesystem Limitation
Prometheus fails when trying to compact/delete old blocks because 9p doesn't support cross-device rename. The `.tmp-for-deletion` pattern fails with "invalid cross-device link". 

**Implication:** Prometheus will work until blocks age, then fail. Wiping data restarts the clock but isn't sustainable.

### Health Check False Positives
Initial health checks showed many services as "520" or "404" — these were false positives. Webhook services return 404 on GET `/` by design; the correct check is GET `/health` or POST to the webhook endpoint.

### Background Workers Misconfigured
Services like `fireflies-poller`, `action-approvals-monitor`, `task-completion-detector` are background workers with no HTTP server. They show 520 because they don't listen on HTTP. Protocol cannot be changed after creation.

## Artifacts

| File | Purpose |
|------|---------|
| `N5/prefs/operations/service-cleanup-protocol.md` | Formal cleanup procedure |
| `N5/config/PORT_REGISTRY.md` | Updated port allocations |
| `N5/logs/maintenance/service-cleanups.jsonl` | Cleanup audit log |
| `N5/builds/service-fixes-2026-01-14/` | Worker assignments (unused) |

## Lessons Learned

1. **Health checks need proper endpoints** — Don't check GET `/` for webhook services
2. **Background workers shouldn't be HTTP services** — Consider TCP protocol or no public endpoint
3. **9p filesystem has limitations** — Not suitable for databases that need rename operations
4. **Service list API caches** — Deletions may not appear immediately

## Follow-Up Items

- [ ] Consider moving Prometheus TSDB to tmpfs (/dev/shm) for reliability
- [ ] Add health endpoints to background workers or convert to TCP
- [ ] Periodic service audit (monthly?) per cleanup protocol

## Tags

#infrastructure #services #cleanup #maintenance #prometheus

