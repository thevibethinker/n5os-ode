---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: pulse:consulting-zoffice-stack:D3.2
---

# Calendly → Zoffice Consultant (Integration)

## What this does
When Calendly sends a webhook (`invitee.created` / `invitee.canceled`), this integration:

- verifies the Calendly webhook signature (if configured)
- creates/updates a consulting session record
- schedules two jobs:
  - **activate** Consultant worker at *(start - 15 min)*
  - **deactivate** Consultant worker at *(end + 30 min)*
- emits notification payloads (prep email + SMS briefing) into a local queue
- logs all actions to the dual-sided audit DB

This is designed to run on **zoputer** (the archetype Zo).

## Calendly setup (manual)
1. Calendly → Integrations → Webhooks
2. Add webhook URL:
   - Recommended: `https://zoputer.zo.computer/api/calendly/webhook`
   - If running as a service: `https://<your-service-domain>/api/calendly/webhook`
3. Subscribe to:
   - `invitee.created`
   - `invitee.canceled`
4. Copy the **Webhook Signing Key**

## Environment variables
- `CALENDLY_WEBHOOK_SIGNING_KEY` — required to verify signatures (recommended)
- `CONSULTING_MANIFEST_PATH` — optional
  - default: `N5/config/consulting/CONSULTING_MANIFEST.md`

## State & outputs
This integration stores state under:
- `N5/config/consulting/calendly_zoffice/`

Key files:
- `sessions.json` — sessions keyed by Calendly scheduled-event URI
- `jobs.json` — activation/deactivation jobs
- `notifications.jsonl` — queued outbound notifications (email + SMS)

## Run modes
### 1) Process a single webhook payload from stdin (dev)
```bash
echo '{"event":"invitee.created","payload":{...}}' | python3 Integrations/calendly-zoffice/scripts/webhook_handler.py --stdin
```

### 2) Run an HTTP server (recommended)
```bash
python3 Integrations/calendly-zoffice/scripts/webhook_handler.py serve --port 8851
# POST /api/calendly/webhook
# GET  /health
```

### 3) Execute due jobs (activation/deactivation)
Run this on a timer (every 1 minute is fine):
```bash
python3 Integrations/calendly-zoffice/scripts/session_prep.py tick
```

## Notes
- This integration **does not send** email/SMS directly; it queues notification payloads in `notifications.jsonl`.
- A separate “notifier” agent/service should deliver those messages using zoputer’s channels.
