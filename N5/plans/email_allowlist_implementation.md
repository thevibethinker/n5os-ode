---
created: 2025-12-16
status: draft
---
# Implementation Plan: Event Allow List System

## Objective
Shift event discovery from "Broad Dragnet" (scanning all newsletters) to a "Curated Allow List" to improve precision and reduce token usage.

## Architecture

### 1. Configuration (`N5/config/event_sources.json`)
The Single Source of Truth for allowed senders.
```json
{
  "senders": [
    "hi@theagentic.ai",
    "newsletter@marvin.vc",
    "events@nextplay.so"
  ],
  "domains": [],
  "last_updated": "2025-12-16"
}
```

### 2. Management Workflow ("The Forward Trigger")
**User Action:** Forward an invite to `va@zo.computer` (or self) with subject `n5:allowlist`.

**System Action (New Hourly Agent):**
1. Scans Gmail for `subject:"n5:allowlist" newer_than:2h`.
2. extract the *original sender* from the forwarded body.
3. Updates `event_sources.json`.
4. Archives the email.

### 3. Discovery Workflow (Daily Morning Agent)
**Current:** Scans city pages via browser.
**New:** Adds Email Scanning Step:
1. **Agent** reads `event_sources.json`.
2. **Agent** constructs query: `from:(sender1 OR sender2...) newer_than:2d`.
3. **Agent** fetches emails via `use_app_gmail` and saves to `N5/data/pending_emails.json`.
4. **Agent** runs `luma_orchestrator.py` which now includes `luma_email_discovery.py` to parse `pending_emails.json`.

## Implementation Checklist
- [ ] Create `N5/config/event_sources.json` with initial seed list.
- [ ] Create `N5/scripts/manage_event_sources.py` (The Manager logic).
- [ ] Create Scheduled Task: "Event Source Manager" (Hourly).
- [ ] Update `N5/scripts/luma_orchestrator.py` to ingest `pending_emails.json`.
- [ ] Update Daily Digest Agent Instruction to perform the email fetch step before running the orchestrator.

