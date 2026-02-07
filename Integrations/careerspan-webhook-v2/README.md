---
created: 2026-01-30
last_edited: 2026-01-30
version: 2.0
provenance: con_BGaXX3RVrXZ0d8T7
---

# Careerspan Webhook Receiver v2

Receives intelligence brief payloads from Dossier AI via their forwarding service.

## Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/webhook` | POST | Bearer | Receive intelligence brief |
| `/health` | GET | None | Health check |

## Authentication

```
Authorization: Bearer YummyYummyDataNomNomNom
```

## Flow

1. **Dossier** calls their `/etc/test_forward_request` endpoint
2. **Their forwarder** POSTs to our `/webhook` with the Bearer token
3. **We validate**, save to inbox, audit log, and notify V
4. **We return** `{ status, filename, timestamp }`
5. **Their forwarder** wraps our response in `{ status_code, response_body }`

## Storage

- **Inbox:** `Careerspan/resumes/inbox/{timestamp}_{candidate-slug}.json`
- **Audit:** `N5/logs/careerspan_webhook_v2.jsonl`

## Service

- **URL:** `https://careerspan-webhook-v2-va.zocomputer.io/webhook`
- **Port:** 8848
- **Runtime:** Bun + Hono

## Testing

```bash
# Health check
curl https://careerspan-webhook-v2-va.zocomputer.io/health

# Test payload
curl -X POST https://careerspan-webhook-v2-va.zocomputer.io/webhook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YummyYummyDataNomNomNom" \
  -d '{
    "candidate": {"name": "Test Candidate", "email": "test@example.com"},
    "role": {"title": "Engineer", "company": "Acme"},
    "overall_assessment": {"score": 85, "bottom_line": "Strong fit"}
  }'
```
