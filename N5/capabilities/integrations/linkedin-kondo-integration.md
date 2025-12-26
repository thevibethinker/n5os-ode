---
created: 2025-10-30
last_edited: 2025-12-11
version: 2.0
capability_id: linkedin-kondo-integration
category: integration
status: active
---

# LinkedIn Intelligence via Kondo

Captures LinkedIn conversation data from Kondo webhooks, stores in SQLite, and integrates with CRM v3 for relationship management.

## What It Does

1. **Receives webhooks** from Kondo when LinkedIn conversations update
2. **Stores conversations & messages** in `Knowledge/linkedin/linkedin.db`
3. **Captures enrichment data**: headlines, locations, connection dates, starred status, notes
4. **Review queue** for contacts not yet in CRM — V approves before CRM creation
5. **Aviato enrichment** for approved contacts — auto-fetches professional intelligence
6. **CRM sync** — links LinkedIn data to existing CRM profiles

## Entry Points

| Type | Path | Description |
|------|------|-------------|
| Webhook | `https://kondo-linkedin-webhook-va.zocomputer.io/webhook` | Receives Kondo data |
| Prompt | `Prompts/LinkedIn Review Queue.prompt.md` | Review pending contacts |
| Script | `N5/scripts/linkedin_review_queue.py` | Manage review queue |
| Script | `N5/scripts/linkedin_approve_and_enrich.py` | Approve + Aviato enrich |
| Script | `N5/scripts/linkedin_crm_sync.py` | Sync to existing CRM profiles |
| Script | `N5/scripts/linkedin_query.py` | Query conversations & stats |

## Associated Files

- **Database**: `Knowledge/linkedin/linkedin.db`
- **Webhook service**: `N5/services/kondo-webhook/index.ts` (v2.0.0)
- **Schema**: `N5/schemas/linkedin_intel.sql`
- **Docs**: `N5/docs/LINKEDIN_INTEGRATION.md`

## Database Tables

| Table | Purpose |
|-------|---------|
| `conversations` | LinkedIn conversation metadata + enrichment |
| `messages` | Individual message content |
| `commitments` | Extracted commitments (future) |
| `crm_review_queue` | Contacts pending CRM approval |
| `processing_log` | Webhook processing audit trail |

## Workflow

```
Kondo Webhook → conversations table (UPSERT)
                    ↓
              Has CRM Profile?
             /              \
           Yes               No
            ↓                 ↓
    Enrich existing    Add to review queue
    CRM profile              ↓
                      V reviews & approves
                             ↓
                      Create CRM profile
                             ↓
                      Aviato enrichment
```

## Changelog

- **v2.0.0** (2025-12-11, con_z8rlwVL5VGt6z0Gk): Added CRM review queue, Aviato enrichment pipeline, expanded enrichment fields (headline, location, connected_at, starred, kondo_note, picture_url)
- **v1.0.0** (2025-10-30): Initial Kondo webhook integration, basic conversation tracking

