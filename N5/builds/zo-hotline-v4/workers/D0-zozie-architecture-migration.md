---
created: 2026-02-17
version: 1.1
provenance: con_D22Ewo8OGuQrMBrx
spawn_mode: manual
status: complete
dependencies:
scope: career-coaching-hotline (NOT zo-hotline)
---
# D0: Zozie Architecture Migration — Dashboard → Code-Controlled

## Objective
Migrate Zozie (Career Coaching Hotline) from VAPI dashboard-owned assistant to the same code-controlled `serverUrl` architecture that Zoseph uses. This ensures both hotlines follow one pattern and all changes happen in code.

## Context
- Zozie's phone (+18574447531) currently uses `assistantId: dd49d3e5-694d-41d3-b273-afe77b2d7862` → VAPI dashboard owns system prompt, model, voice, tools
- Zoseph's phone (+18788792087) uses `server.url` → webhook returns full assistant config dynamically via `assistant-request`
- The career coaching webhook (`vapi-webhook` on port 4242) ALREADY has a full `assistant-request` handler that returns the complete assistant config — it's just never called
- The dashboard system prompt is 26,440 chars (~4,260 words) — much larger than the webhook's version

## Pre-Work Already Done (by orchestrator)
All dashboard state has been snapshotted to `N5/builds/zo-hotline-v4/workers/`:
- `zozie-dashboard-snapshot.json` — Full assistant config from VAPI API
- `zozie-dashboard-system-prompt.md` — The 26K-char system prompt
- `zozie-dashboard-tools.json` — All 6 tool definitions with parameters
- `zozie-phone-config.json` — Phone number routing config
- `zoseph-phone-config.json` — Reference: how Zoseph's phone is configured (the target pattern)

## Steps

### 1. Reconcile Dashboard vs Webhook
Compare the dashboard assistant config (`zozie-dashboard-snapshot.json`) against what the webhook's `assistant-request` handler currently returns:
- System prompt: dashboard has 26K chars, webhook has its own version — which is more current?
- Tools: dashboard has 6 tools, webhook has 11 (6 original + 5 new) — webhook is ahead
- Voice config: compare stability, style, voiceId values
- Transcriber keywords: compare lists
- First message: compare text
- Latency params: startSpeakingPlan, stopSpeakingPlan, chunkPlan

**Decision needed:** Is the webhook version the canonical one? If so, the dashboard version is a stale snapshot and we just need to verify nothing is missing.

### 2. Update Phone Number Config
Use VAPI API to switch Zozie's phone from `assistantId` to `serverUrl`:
```bash
curl -X PATCH "https://api.vapi.ai/phone-number/474c2e31-38a7-4f6d-bdfd-89d83d366c84" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "assistantId": null,
    "serverUrl": "https://vapi-webhook-va.zocomputer.io"
  }'
```
**⚠️ This is the live switch.** After this, the webhook handles everything.

### 3. Test Call
Call +18574447531 and verify:
- First message plays (from webhook, not dashboard)
- Tool calls work (assessment, recommendations, concept lookup)
- End-of-call report logs correctly
- SMS notification fires

### 4. Clean Up Dead References
- The phone's `server.url` currently points to `career-coaching-hotline-va.zocomputer.io` (port 8848, now deleted) — this gets replaced in Step 2
- The dashboard assistant (`dd49d3e5`) can be left in place as a reference or deleted — V's call

## Acceptance Criteria
- [ ] Zozie phone uses `serverUrl` (no `assistantId`)
- [ ] Test call completes successfully with tools working
- [ ] Dashboard prompt preserved in snapshot files (already done)
- [ ] Both hotlines now follow identical architecture pattern

## Risk
- **LOW**: The webhook already handles `assistant-request` and returns full config
- **ROLLBACK**: Re-add `assistantId` to phone config via API (takes 10 seconds)

## Files to Reference
- `Skills/career-coaching-hotline/scripts/hotline-webhook.ts` (⚠️ n5_protected — PII flag)
- `N5/builds/zo-hotline-v4/workers/zozie-dashboard-snapshot.json`
- `N5/builds/zo-hotline-v4/workers/zoseph-phone-config.json` (target pattern reference)

## Completion Summary (2026-02-17 22:00 ET)

- ✅ Zozie phone switched from `assistantId` → `serverUrl` (https://vapi-webhook-va.zocomputer.io)
- ✅ Dashboard assistant preserved (not deleted) as reference
- ✅ Test call confirmed: assistant-request handled by webhook, 30s call completed
- ✅ End-of-call report received and logged
- ✅ Dashboard snapshots preserved in this workers/ folder
- ⚠️ Transient DuckDB lock contention observed (resolved on its own)
- ⚠️ Webhook auth currently DISABLED on vapi-webhook — should be re-enabled
