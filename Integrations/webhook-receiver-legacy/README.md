---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
---

# Webhook Receiver

Simple webhook receiver service for accepting POST requests from Zapier.

## Endpoints

- **POST /webhook** - Main webhook endpoint (use this URL in Zapier)
- **GET /logs** - View recent webhook payloads
- **GET /health** - Health check endpoint

## Features

- Accepts JSON and form-urlencoded data
- Logs all incoming webhooks to `webhook-logs.jsonl`
- Returns success confirmation to Zapier
- View logs via `/logs` endpoint

## Logs

All webhook data is stored in `webhook-logs.jsonl` with:
- Timestamp
- Headers
- Body payload
- Query parameters

## Usage in Zapier

1. Use the public URL provided when the service is registered
2. Configure Zapier to POST to: `https://your-url/webhook`
3. Zapier will receive a 200 OK response with JSON confirmation

