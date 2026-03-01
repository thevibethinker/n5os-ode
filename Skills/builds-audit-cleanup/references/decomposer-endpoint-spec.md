---
created: 2026-01-31
last_edited: 2026-01-31
version: 1.0
provenance: con_UrFALeCPJY7CTOAD
---

# Careerspan Decomposer Endpoint Specification

## Overview

Webhook endpoint for receiving Careerspan intelligence data and triggering the decomposer → meta-resume-generator pipeline. This endpoint replaces the current file-based input model with a push-based API model.

## Current State

- **Current Mode:** Manual file-based ingestion via `careerspan-decomposer` skill
- **Current Command:** `python3 Skills/careerspan-decomposer/scripts/decompose.py --doc <file> --jd <file> --candidate <name> --company <company>`
- **Existing v2 Webhook:** `careerspan-webhook-v2` on port 8847 (in `Integrations/careerspan-webhook-v2/`) - currently just saves to inbox without triggering decomposer

## Target State

Careerspan system pushes intelligence data → Webhook validates → Trigger decomposer → Output meta-resume PDF → Deliver to client

---

## 1. Endpoint Design

### URL Pattern
```
POST /webhooks/careerspan/decompose
```

### Authentication
**Method:** Bearer Token in Authorization header

```http
Authorization: Bearer <CAREERSPAN_WEBHOOK_TOKEN>
```

**Implementation Options:**
1. **Simple (current v2 pattern):** Static token stored in environment variable `CAREERSPAN_WEBHOOK_TOKEN`
2. **Enhanced:** HMAC signature verification (Svix-style) for production security

**Recommendation:** Start with simple Bearer token (matches existing careerspan-webhook-v2 pattern), upgrade to Svix if needed for production.

### HTTP Methods
- `POST /webhooks/careerspan/decompose` - Main endpoint
- `GET /health` - Health check (no auth)

---

## 2. Payload Schema

### Required Fields

```json
{
  "candidate": {
    "name": "<full name>"
  },
  "role": {
    "title": "<job title>",
    "company": "<company name>"
  },
  "careerspan_doc": "<full text or URL to careerspan brief>",
  "job_description": "<full text or URL to JD>"
}
```

### Optional Fields

```json
{
  "candidate": {
    "name": "<full name>",
    "email": "<email address>"
  },
  "role": {
    "title": "<job title>",
    "company": "<company name>"
  },
  "careerspan_doc": "<full text or URL>",
  "careerspan_doc_url": "<alternative URL field>",
  "job_description": "<full text or URL>",
  "job_description_url": "<alternative URL field>",
  "overall_assessment": {
    "score": 89,
    "qualification": "Well-aligned",
    "bottom_line": "Strong candidate with relevant experience"
  },
  "metadata": {
    "request_id": "<unique identifier>",
    "submitted_at": "<ISO timestamp>",
    "source": "careerspan-api|manual"
  }
}
```

### Field Types

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `candidate.name` | string | Yes | Full candidate name (used for output folder naming) |
| `candidate.email` | string | No | Candidate email (optional) |
| `role.title` | string | Yes | Job title |
| `role.company` | string | Yes | Company name |
| `careerspan_doc` | string | Yes* | Full text of Careerspan brief OR use `careerspan_doc_url` |
| `careerspan_doc_url` | string | Yes* | URL to fetch brief (alternative to text) |
| `job_description` | string | Yes* | Full text of JD OR use `job_description_url` |
| `job_description_url` | string | Yes* | URL to fetch JD (alternative to text) |
| `overall_assessment.score` | integer | No | Overall score (0-100) - if provided, used for validation |
| `overall_assessment.bottom_line` | string | No | Bottom line assessment |
| `metadata.request_id` | string | No | Unique ID for deduplication |

*At least one of text or URL must be provided for each document.

### Example Full Payload

```json
{
  "candidate": {
    "name": "Jane Doe",
    "email": "jane.doe@example.com"
  },
  "role": {
    "title": "Senior Software Engineer",
    "company": "TechCorp"
  },
  "careerspan_doc": "Referred 89 © Applied Jan 26, 2026\n\n[Full brief text here...]",
  "job_description": "We are looking for a Senior Software Engineer...\n\n[Full JD text here...]",
  "overall_assessment": {
    "score": 89,
    "qualification": "Well-aligned",
    "bottom_line": "Strong technical background with 8 years experience"
  },
  "metadata": {
    "request_id": "req_2026-01-31_jane-doe-techcorp",
    "submitted_at": "2026-01-31T19:30:00Z",
    "source": "careerspan-api"
  }
}
```

---

## 3. Processing Flow

```
┌─────────────────┐
│ Careerspan      │
│ System          │
└────────┬────────┘
         │ POST /webhooks/careerspan/decompose
         │ with Bearer token
         ▼
┌─────────────────────────────────┐
│ 1. Validate Request            │
│    - Check auth token          │
│    - Validate required fields  │
│    - Check document content     │
└────────┬──────────────────────┘
         │ Valid?
         │ No → 400/401 error
         │ Yes ↓
┌─────────────────────────────────┐
│ 2. Store Raw Data             │
│    - Save JSON to inbox        │
│    - Write audit log entry     │
│    - Extract/copy JD           │
└────────┬──────────────────────┘
         ▼
┌─────────────────────────────────┐
│ 3. Trigger Decomposer         │
│    - Call decompose.py         │
│    - Pass doc + JD paths      │
│    - Wait for completion      │
└────────┬──────────────────────┘
         ▼
┌─────────────────────────────────┐
│ 4. Validate Output           │
│    - Check canonical_schema    │
│    - Verify all files present  │
│    - Validate scores_complete  │
└────────┬──────────────────────┘
         │ Valid?
         │ No → Error response + audit
         │ Yes ↓
┌─────────────────────────────────┐
│ 5. Trigger Meta-Resume        │
│    - Call meta-resume-generator│
│    - Generate PDF             │
│    - Store output             │
└────────┬──────────────────────┘
         ▼
┌─────────────────────────────────┐
│ 6. Respond to Careerspan     │
│    - Return 200 with details  │
│    - Include output location  │
│    - Send notification        │
└─────────────────────────────────┘
```

### Detailed Steps

#### Step 1: Validate Request
- Check `Authorization` header matches `CAREERSPAN_WEBHOOK_TOKEN`
- Validate required fields: `candidate.name`, `role.title`, `role.company`
- Ensure at least one of `careerspan_doc`/`careerspan_doc_url` is present
- Ensure at least one of `job_description`/`job_description_url` is present
- If `overall_assessment.score` provided, validate it's 0-100

**Error Responses:**
- `401 Unauthorized` - Invalid or missing auth token
- `400 Bad Request` - Missing required fields, invalid JSON, or document fetch failure

#### Step 2: Store Raw Data
- Create inbox folder: `Careerspan/meta-resumes/inbox/<candidate>-<company>/`
- Save raw payload as `_incoming_webhook.json` with metadata:
  ```json
  {
    "_meta": {
      "received_at": "<ISO timestamp>",
      "source": "careerspan-webhook",
      "request_id": "<from payload>",
      "webhook_event_id": "<internal ID>"
    },
    ...original payload
  }
  ```
- If URL provided, fetch and save content:
  - Save `careerspan_full_ocr.txt` from `careerspan_doc_url`
  - Save `jd.yaml` from `job_description_url`
- Write audit log entry to `N5/logs/careerspan_webhook_audit.jsonl`

#### Step 3: Trigger Decomposer
- Extract candidate slug: `candidate.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')`
- Extract company slug: `role.company.toLowerCase().replace(/[^a-z0-9]+/g, '-')`
- Call decomposer:
  ```bash
  python3 Skills/careerspan-decomposer/scripts/decompose.py \
    --doc /path/to/careerspan.txt \
    --jd /path/to/jd.yaml \
    --candidate <candidate> \
    --company <company>
  ```
- Wait for completion (timeout: 5 minutes)

#### Step 4: Validate Output
- Run validation script:
  ```bash
  python3 Skills/careerspan-decomposer/scripts/validate.py <candidate>-<company>
  ```
- Check that canonical schema validation passes
- Verify `scores_complete.json` exists and is valid
- Confirm all expected YAML files are present

If validation fails:
- Return `500 Internal Server Error`
- Include validation error details
- Log to audit log as `validation_failed`

#### Step 5: Trigger Meta-Resume Generator
- Call meta-resume generator:
  ```bash
  python3 Skills/meta-resume-generator/scripts/generate.py \
    --inbox <candidate>-<company>
  ```
- Generate PDF with Careerspan branding
- Store output in `Careerspan/meta-resumes/outbox/`

#### Step 6: Respond and Notify
- Return `200 OK` with:
  ```json
  {
    "status": "processed",
    "request_id": "<from payload>",
    "candidate": "<name>",
    "company": "<company>",
    "score": <score from decomposer>,
    "pdf_path": "<path to generated PDF>",
    "output_folder": "<path to inbox folder>",
    "timestamp": "<ISO timestamp>"
  }
  ```
- Send email notification to V with summary
- If configured, send webhook callback to Careerspan system

---

## 4. Implementation Notes

### Port Allocation
**Current port allocation in PORT_REGISTRY.md:**
- Port 8847: `careerspan-webhook` (existing v2 webhook)

**Recommendation:** 
- **Option 1 (Simple):** Reuse port 8847, replace `careerspan-webhook-v2` with new decomposer endpoint
- **Option 2 (Parallel):** Use next available webhook port: 8848

**Decision:** Use port 8848 for new decomposer endpoint, keep v2 webhook running as fallback during migration.

Update PORT_REGISTRY.md:
```markdown
| 8847 | careerspan-webhook-v2 | http | service | Legacy Careerspan data webhook |
| 8848 | careerspan-decompose | http | service | Careerspan decomposer endpoint |
```

### Service Registration Approach

**Framework:** FastAPI (Python) or Hono (Bun)

**Recommendation:** Use FastAPI to match existing webhook patterns (recall-webhook, fathom-webhook, fireflies-webhook) and for easy integration with decomposer scripts.

**Directory Structure:**
```
Integrations/careerspan-decompose-webhook/
├── server.py              # Main FastAPI application
├── config.py              # Config (tokens, paths)
├── processor.py           # Main processing logic
├── models.py              # Pydantic models for validation
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

**Service Registration:**
```bash
# Register service
register_user_service \
  --label "careerspan-decompose" \
  --protocol http \
  --local_port 8848 \
  --workdir /home/workspace/Integrations/careerspan-decompose-webhook \
  --entrypoint "python3 server.py"
```

### Error Handling

#### Retry Strategy
- **Transient errors** (network, fetch failures): Retry 3 times with exponential backoff
- **Decomposer failures**: Log error, return 500, do NOT retry (manual review needed)
- **Validation failures**: Return 400 with details, do NOT retry

#### Logging
- All requests logged to `N5/logs/careerspan_decompose_webhook.jsonl`
- Entry format:
  ```json
  {
    "ts": "<ISO timestamp>",
    "event": "<received|processed|error|validation_failed>",
    "request_id": "<id>",
    "candidate": "<name>",
    "company": "<company>",
    "status": "<success|error>",
    "error": "<error message if failed>",
    "processing_time_ms": <duration>,
    "output_path": "<path if successful>"
  }
  ```

#### Alerts
- **Auth failures** (>5 in 5 min): SMS alert
- **Validation failures** (>3 in 1 hour): Email alert
- **Processing failures** (any): SMS alert with error details

### Environment Variables

```bash
# Authentication
CAREERSPAN_WEBHOOK_TOKEN="your-secret-token-here"

# Paths
INBOX_PATH="/home/workspace/Careerspan/meta-resumes/inbox"
OUTBOX_PATH="/home/workspace/Careerspan/meta-resumes/outbox"
AUDIT_LOG="/home/workspace/N5/logs/careerspan_decompose_webhook.jsonl"

# API endpoints (for callbacks)
CAREERSPAN_CALLBACK_URL="https://careerspan.example.com/api/callback"
ZO_API_TOKEN="${ZO_CLIENT_IDENTITY_TOKEN}"

# timeouts
FETCH_TIMEOUT_SECONDS=30
DECOMPOSE_TIMEOUT_SECONDS=300
```

### Async Processing

For long-running decomposer/generation tasks, consider async pattern:

```python
from fastapi import BackgroundTasks

@app.post("/webhooks/careerspan/decompose")
async def receive_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    # 1. Quick validation
    # 2. Save raw data
    # 3. Return 202 Accepted with job_id
    # 4. Background task runs decomposer → generator
    job_id = str(uuid.uuid4())
    background_tasks.add_task(process_async, job_id, payload)
    return {"status": "accepted", "job_id": job_id}
```

**Recommendation:** Start with synchronous processing (simpler), add async if timeouts become an issue.

### Dependencies

**requirements.txt:**
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
aiohttp>=3.9.0
jsonschema>=4.20.0
```

---

## 5. Security Considerations

1. **Authentication:**
   - Use strong random Bearer token (32+ chars)
   - Store token as secret in Settings > Developers
   - Rotate tokens quarterly

2. **Input Validation:**
   - Limit payload size: max 10MB
   - Sanitize file paths (prevent directory traversal)
   - Validate URLs allowlist (if using URL fetching)

3. **Rate Limiting:**
   - Max 100 requests/minute per IP
   - Max 1000 requests/hour total

4. **Audit Trail:**
   - Log all requests with timestamps
   - Include request_id for traceability
   - Retain logs for 90 days

---

## 6. Testing Plan

### Unit Tests
- [ ] Token validation
- [ ] Required field validation
- [ ] URL fetching with timeout handling
- [ ] Payload size limits

### Integration Tests
- [ ] Full flow: webhook → decompose → validate → generate
- [ ] Error cases: missing fields, invalid auth, decomposer failure
- [ ] Async processing (if implemented)

### Manual Testing
- [ ] Test with real Careerspan payload
- [ ] Verify PDF output matches expectations
- [ ] Test notification delivery
- [ ] Load test with 10 concurrent requests

---

## 7. Migration Path

### Phase 1: Deploy New Endpoint (Current Task)
- Implement decomposer webhook on port 8848
- Test with Careerspan team
- Keep v2 webhook running as backup

### Phase 2: Gradual Cutover
- Careerspan switches to new endpoint for 10% of traffic
- Monitor for errors
- Gradually increase to 50%, then 100%

### Phase 3: Deprecation
- After 2 weeks of stable operation, decommission v2 webhook
- Update documentation
- Port 8847 can be reassigned or kept as fallback

---

## 8. Implementation Complexity Assessment

**Overall Complexity: Medium**

| Component | Complexity | Notes |
|-----------|------------|-------|
| FastAPI server | Low | Standard webhook pattern, similar to recall-webhook |
| Auth/validation | Low | Simple Bearer token, Pydantic models |
| Document fetching | Low | Use aiohttp with timeout |
| Decomposer integration | Medium | Need robust subprocess handling, timeout management |
| Output validation | Medium | Reuse existing validate.py, error handling |
| Meta-resume generation | Low | Call existing skill script |
| Error handling | Medium | Need comprehensive logging and alerts |
| Async processing | Low (optional) | BackgroundTasks if needed |

**Estimated Implementation Time:** 4-6 hours

**Key Risks:**
1. Decomposer timeout - long briefs may exceed 5 min
2. PDF generation failures - need manual review path
3. Careerspan payload format changes - maintain flexibility

**Mitigations:**
1. Implement async processing for long jobs
2. Add manual trigger endpoint for reprocessing
3. Use loose validation, accept varied payload structures
