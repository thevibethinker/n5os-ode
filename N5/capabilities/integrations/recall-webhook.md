---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_2am5bxIzjC2JGV3F
---

# Recall.ai Webhook Receiver

```yaml
capability_id: recall-webhook
name: "Recall.ai Webhook Receiver"
category: integration
status: active
confidence: high
last_verified: 2026-01-24
tags:
  - meetings
  - transcripts
  - recordings
  - webhooks
entry_points:
  - type: script
    id: "Integrations/recall_ai/webhook_receiver.py"
  - type: script
    id: "Integrations/recall_ai/recall_client.py"
  - type: script
    id: "Integrations/recall_ai/meeting_depositor.py"
  - type: url
    value: "https://recall-webhook-va.zocomputer.io/webhook/recall"
owner: "V"
replaces: "fireflies-webhook"
```

## What This Does

Receives real-time webhook notifications from Recall.ai when meeting bots complete their recordings. Automatically downloads recordings (audio + video), transcripts, and participant events, then deposits them into the meeting pipeline following the meeting-queue-protocol.

**Replaces Fireflies.ai** - This is the new primary meeting recording integration.

## Key Features

- **Automatic deposit**: When bot.done event received, downloads all artifacts and creates meeting folder
- **Classification**: Automatically classifies meetings as internal/external
- **Video retention**: 180-day retention on video recordings
- **Full artifacts**: Audio, video, transcript, and participant events
- **Deduplication**: Checks for existing meetings before depositing

## How to Use It

### 1. Create a bot to join a meeting

```bash
python3 Integrations/recall_ai/recall_client.py create-bot "https://zoom.us/j/123456789"
```

### 2. For scheduled meetings (10+ min in future)

```bash
python3 Integrations/recall_ai/recall_client.py create-bot "https://meet.google.com/abc" --join-at "2026-01-25T14:00:00Z"
```

### 3. Webhook handles the rest

When the meeting ends, Recall.ai sends a webhook → bot artifacts are downloaded → meeting folder is created in `Personal/Meetings/`.

## CLI Commands

```bash
# Test API connection
python3 Integrations/recall_ai/recall_client.py test

# Create bot (ad-hoc)
python3 Integrations/recall_ai/recall_client.py create-bot <meeting_url>

# Create scheduled bot
python3 Integrations/recall_ai/recall_client.py create-bot <meeting_url> --join-at <iso_timestamp>

# List bots
python3 Integrations/recall_ai/recall_client.py list-bots --limit 10

# Get bot details
python3 Integrations/recall_ai/recall_client.py get-bot <bot_id>

# Manual download (if webhook missed)
python3 Integrations/recall_ai/recall_client.py download <bot_id> --output-dir /path/to/output

# Manual deposit
python3 Integrations/recall_ai/meeting_depositor.py <bot_id>
```

## Associated Files & Assets

- `file 'Integrations/recall_ai/README.md'` – Full documentation
- `file 'Integrations/recall_ai/config.py'` – Configuration and defaults
- `file 'Integrations/recall_ai/recall_client.py'` – REST API client
- `file 'Integrations/recall_ai/webhook_receiver.py'` – FastAPI webhook server
- `file 'Integrations/recall_ai/meeting_depositor.py'` – Meeting pipeline integration
- `file 'N5/data/recall_webhooks.db'` – SQLite database for webhook events

## Webhook Configuration

**URL**: `https://recall-webhook-va.zocomputer.io/webhook/recall`

Configure this URL in the Recall.ai dashboard under Webhooks.

## Workflow

```mermaid
flowchart TD
  A[Calendar Event] --> B[Create Bot via API]
  B --> C[Bot Joins Meeting]
  C --> D[Meeting Ends]
  D --> E[Recall.ai sends bot.done webhook]
  E --> F[Webhook Receiver]
  F --> G[Download artifacts]
  G --> H[Create meeting folder]
  H --> I[Personal/Meetings/YYYY-MM-DD_{title}/]
```

## Environment Variables

```bash
RECALL_API_KEY=<api-key>           # Required
RECALL_REGION=us-west-2            # Default region
RECALL_WEBHOOK_SECRET=<secret>     # Optional, for signature verification
```

## Service Details

| Property | Value |
|----------|-------|
| Port | 8846 |
| Service Label | recall-webhook |
| Protocol | HTTP |
| Public URL | https://recall-webhook-va.zocomputer.io |

## Notes / Gotchas

- Video recordings have 180-day retention (configurable via `video_retention_period` in config)
- For scheduled bots, `join_at` must be 10+ minutes in the future
- Ad-hoc bots (no `join_at` or <10 min future) join immediately
- Webhook must respond quickly (<500ms) to avoid retries
- If webhook misses an event, use manual download + deposit commands

## Migration from Fireflies

1. This integration replaces `fireflies-webhook` (port 8420)
2. Same meeting folder structure in `Personal/Meetings/`
3. Same classification logic (internal/external)
4. Adds video recording (Fireflies was audio-only)
