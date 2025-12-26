---
created: 2025-12-11
last_edited: 2025-12-11
version: 1.0
---

# AAR: Kondo LinkedIn CRM Review Queue Enhancement

**Conversation:** `con_z8rlwVL5VGt6z0Gk`  
**Date:** 2025-12-10 → 2025-12-11  
**Type:** Build  
**Capability:** `linkedin-kondo-integration` v1.0 → v2.0

## Summary

Enhanced the Kondo/LinkedIn integration with a CRM review queue system, Aviato enrichment pipeline, and expanded webhook data capture. V can now review LinkedIn contacts before adding to CRM, with automatic Aviato professional intelligence enrichment on approval.

## What Was Built

### 1. Webhook Handler v2.0.0
- **File:** `N5/services/kondo-webhook/index.ts`
- **Changes:** Added capture for `connected_at`, `contact_headline`, `contact_location`, `contact_picture_url`, `kondo_note`, `starred`
- Auto-adds unmatched contacts to review queue

### 2. CRM Review Queue System
- **Script:** `N5/scripts/linkedin_review_queue.py`
- **Table:** `crm_review_queue` in `linkedin.db`
- **Commands:** `scan`, `digest`, `approve`, `reject`, `ignore`, `approved`
- Prevents "bozos" from auto-entering CRM

### 3. Approve & Enrich Pipeline
- **Script:** `N5/scripts/linkedin_approve_and_enrich.py`
- Creates CRM profile on approval
- Auto-enriches with Aviato API
- Links LinkedIn conversation to CRM profile

### 4. CRM Sync Script
- **Script:** `N5/scripts/linkedin_crm_sync.py`
- Enriches existing CRM profiles with LinkedIn data
- Additive only — never deletes existing profile data

### 5. Prompt
- **File:** `Prompts/LinkedIn Review Queue.prompt.md`
- Quick access to review pending contacts

### 6. Database Schema Enhancements
- Added 6 columns to `conversations` table
- Created `crm_review_queue` table with UNIQUE constraint on `conversation_id`

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Review queue instead of auto-CRM | V doesn't want every LinkedIn contact in CRM |
| UPSERT deduplication | Prevents duplicates on bulk sync |
| Aviato on approval only | Cost control — only enrich approved contacts |
| Additive CRM sync | Never delete existing profile intelligence |

## Debugging Performed

1. **Initial issue:** "No messages since Dec 4th" — diagnosed as Kondo not sending webhooks (quiet inbox, not a bug)
2. **Bulk sync:** Triggered from Kondo to populate enrichment fields
3. **Deduplication audit:** Fixed race conditions, added UNIQUE constraints, verified no duplicates after bulk sync

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Conversations | 145 | 200 |
| With headlines | 0 | 143 (72%) |
| With connected_at | 0 | 62 (31%) |
| Starred | — | 11 |
| Review queue | — | 142 pending |

## Lessons Learned

1. **Kondo is event-driven** — only sends webhooks on new activity, not a continuous sync
2. **Deduplication must be multi-layered** — webhook, scan script, and profile creation all need guards
3. **Review queue pattern** — good for any integration where you want human gatekeeping before CRM entry

## Open Items

- [ ] Set up scheduled digest (V planning unified system digest in separate conversation)
- [ ] Kondo API is read-only — cannot add/remove stars programmatically

## Files Modified/Created

```
N5/services/kondo-webhook/index.ts (modified → v2.0.0)
N5/scripts/linkedin_review_queue.py (created)
N5/scripts/linkedin_approve_and_enrich.py (created)
N5/scripts/linkedin_crm_sync.py (created)
Prompts/LinkedIn Review Queue.prompt.md (created)
N5/capabilities/integrations/linkedin-kondo-integration.md (created)
Knowledge/linkedin/linkedin.db (schema modified)
Integrations/Aviato (symlink created)
```

