---
title: Calendly
description: Manage Calendly integration — OAuth, links, webhooks, and CRM intake
tags: [calendly, scheduling, crm, integration, tool]
tool: true
created: 2026-01-15
last_edited: 2026-01-16
version: 2.1
provenance: con_Ok7qEYOax94psy7F
---

# Calendly Integration

OAuth-authenticated integration with Calendly API v2. Handles scheduling links and CRM intake for new bookings.

## Architecture

```
Calendly Booking → Webhook → CRM Profile + Enrichment Queue
                              ↓
                    Gmail search (prior contact?)
                    Aviato/LinkedIn enrichment
                    DD prep for meeting
```

**Key insight:** Calendly is the CRM gatekeeper, not the meeting folder creator. Transcripts (Fireflies, Granola, manual) create meeting folders.

## Commands

### Verify Connection
```bash
python3 Integrations/calendly/calendly_cli.py verify
```

### List Scheduling Links
```bash
python3 Integrations/calendly/calendly_cli.py links --list
```

### View Upcoming Events
```bash
python3 Integrations/calendly/calendly_cli.py events --upcoming
```

### Webhook Management
```bash
# List registered webhooks
python3 Integrations/calendly/calendly_cli.py webhooks --list

# Register webhook (if not already registered)
python3 Integrations/calendly/calendly_cli.py webhooks --register
```

### Sync Links to Content Library
```bash
python3 Integrations/calendly/sync_links.py
```

## Webhook Flow (invitee.created)

When someone books a meeting:

1. **CRM Profile Creation/Update**
   - Check if profile exists by email
   - Create new profile if needed
   - Infer category from event type (INVESTOR, ADVISOR, COMMUNITY, NETWORKING)

2. **Enrichment Queue**
   - Queue checkpoint_2 (Aviato, LinkedIn)
   - Queue checkpoint_gmail (search for prior email threads)

3. **Meeting Context**
   - Append booking details to profile YAML
   - Event type, scheduled time, source

## Files

- `file 'Integrations/calendly/server.ts'` — OAuth + webhook service
- `file 'Integrations/calendly/calendly_client.py'` — API client with token auto-refresh
- `file 'Integrations/calendly/calendly_cli.py'` — CLI tool
- `file 'Integrations/calendly/crm_intake.py'` — CRM profile creation + enrichment
- `file 'Integrations/calendly/sync_links.py'` — Content Library sync
- `file 'Knowledge/content-library/links/calendly/'` — Synced scheduling links

## Service

- **URL:** https://calendly-auth-va.zocomputer.io
- **Port:** 50001
- **Endpoints:**
  - `/` — OAuth authorization flow
  - `/callback` — OAuth callback
  - `/webhook` — Calendly webhook receiver
  - `/health` — Health check

## Re-Authorization

If tokens expire or you need to reconnect:
1. Go to https://calendly-auth-va.zocomputer.io
2. Click "Connect Calendly"
3. Authorize the app
