---
created: 2026-02-02
last_edited: 2026-02-02
version: 1.0
provenance: con_NLOu2MVInIYnuwuf
---

# Careerspan Intelligence Brief Webhook

Receives Intelligence Briefs when candidates complete their Careerspan Stories.

## Purpose

When a candidate completes their Careerspan Stories, this webhook receives the Intelligence Brief payload and triggers the downstream pipeline:

1. **Receive** → Intelligence Brief data (JSON or PDF)
2. **Decompose** → Run `careerspan-decomposer` skill to extract structured YAML
3. **Generate** → Run `meta-resume-generator` skill to create Candidate:Decoded PDF
4. **Upload** → Push to Google Drive shared folder
5. **Notify** → Email Shivam with the deliverable

## Webhook Endpoint

**URL:** `https://va.zo.computer/webhooks/careerspan-brief`
**Method:** POST
**Auth:** Bearer token (configured in Careerspan admin)

## Expected Payload

```json
{
  "event": "brief_completed",
  "candidate": {
    "id": "...",
    "name": "...",
    "email": "..."
  },
  "job_opening": {
    "id": "...",
    "title": "...",
    "company": "..."
  },
  "brief": {
    "score": 89,
    "url": "https://...",  // Download URL for full brief
    "data": { ... }        // Or inline structured data
  },
  "org_id": "corridorx.io",
  "timestamp": "2026-02-02T16:30:00Z"
}
```

## Configuration

Before enabling:
1. Set `CAREERSPAN_WEBHOOK_SECRET` in Zo secrets
2. Register webhook URL in Careerspan admin for corridorx.io org
3. Verify `corridorx_account_id` is set in pipeline config

## Files

| File | Purpose |
|------|---------|
| `webhook_receiver.py` | HTTP server receiving POST requests |
| `brief_processor.py` | Orchestrates decompose → generate → upload flow |
| `config.yaml` | Webhook-specific config (inherits from pipeline) |

## Related

- Parent pipeline: `Integrations/careerspan-pipeline/`
- Decomposer skill: `Skills/careerspan-decomposer/`
- Meta-resume skill: `Skills/meta-resume-generator/`
