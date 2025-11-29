---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Fireflies Webhook Receiver

```yaml
capability_id: fireflies-webhook
name: "Fireflies Webhook Receiver"
category: integration
status: active
confidence: medium
last_verified: 2025-11-29
tags:
  - meetings
  - transcripts
  - webhooks
entry_points:
  - type: script
    id: "N5/services/fireflies_webhook/webhook_receiver.py"
  - type: script
    id: "N5/services/fireflies_webhook/processor.py"
  - type: url
    value: "https://va.zo.computer/webhook/fireflies"
owner: "V"
```

## What This Does

Receives real-time webhook notifications from Fireflies.ai when meeting transcripts are completed and logs them into a local SQLite database for further processing inside the N5 meeting pipeline.

## How to Use It

- Configure Fireflies.ai to send webhooks to the `/webhook/fireflies` endpoint on this Zo computer.
- Ensure the service is running as a Zo user service or a background uvicorn process.
- Downstream scripts can query `N5/data/fireflies_webhooks.db` to pull pending or recent webhook events into the meeting pipeline.

## Associated Files & Assets

- `file 'N5/services/fireflies_webhook/README.md'` – Service documentation and setup
- `file 'N5/services/fireflies_webhook/webhook_receiver.py'` – FastAPI app entrypoint
- `file 'N5/services/fireflies_webhook/processor.py'` – Processing logic for stored webhooks
- `file 'N5/data/fireflies_webhooks.db'` – SQLite database for webhook events

## Workflow

```mermaid
flowchart TD
  A[Fireflies.ai Transcript Completed] --> B[POST /webhook/fireflies]
  B --> C[Webhook Receiver (FastAPI)]
  C --> D[Persist event to fireflies_webhooks.db]
  D --> E[Downstream meeting pipeline scripts]
```

## Notes / Gotchas

- Webhook HMAC signature verification is optional but recommended; ensure `FIREFLIES_WEBHOOK_SECRET` is configured.
- Service must respond quickly (<500ms) to avoid Fireflies retries or failures.
- Database file location `/home/workspace/N5/data/fireflies_webhooks.db` must be writable by the service process.

