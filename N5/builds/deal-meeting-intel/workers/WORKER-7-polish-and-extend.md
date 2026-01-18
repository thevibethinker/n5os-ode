---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_GCktM2iwLZIi5cHK
worker_id: 7
title: Polish & Extend - Notion Workaround, SMS Commands, B37 Template, Email Backfill
est_time: 2 hours
depends_on: [1, 2, 3, 4, 5, 6]
status: ready
---

# Worker 7: Polish & Extend

## Context Summary

**Build Status:** Deal Intelligence System is COMPLETE (79 tests passing, 6 workers done).

**What Was Built:**
- Signal Router (`N5/scripts/deal_signal_router.py`) — LLM-assisted deal matching
- B37 Generator (`N5/scripts/meeting_deal_intel.py`) — Meeting → deal intel blocks
- Notion Sync (`N5/scripts/notion_deal_sync.py`) — Bidirectional sync with field mapping
- SMS Handler (`N5/scripts/sms_deal_handler.py`) — "n5 deal" commands
- Email Scanner (`N5/scripts/email_deal_scanner.py`) — Gmail deal signal extraction
- Proactive Sensor (`N5/scripts/deal_proactive_sensor.py`) — New entity detection + SMS approval

**Database:**
- 77 deals (52 Careerspan acquirers + 25 Zo partnerships)
- 32 contacts (11 brokers + 21 leadership)
- Tables: `deals`, `deal_contacts`, `deal_activities`, `processed_emails`, `pending_approvals`, `notion_outbox`, `notion_sync_state`

**Notion Databases (via Pipedream):**
- Acquirer Targets: `3a2d606f-99fb-4ecf-9f92-374d324f7247`
- Leadership Targets: `2438ec09-5208-45d5-88b3-2d761099da9a`
- Deal Brokers: `2ec5c3d6-a5db-8007-a821-000bf97dee8b`
- Field mapping: `file 'N5/config/notion_field_mapping.json'`

---

## Task 1: Notion Append Workaround

### Problem
`notion-append-block` returns "Unknown error" — can't append content to pages.

### Solution: Read-Modify-Write Pattern

Instead of appending, we:
1. Read the current "Notes" or "Intelligence Summary" field
2. Prepend new content to existing content
3. Write back the combined content

### Implementation

Update `N5/scripts/notion_deal_sync.py` to add a `prepend_intel` function:

```python
def prepend_intel_to_page(
    notion_page_id: str,
    field_name: str,  # "Notes" or "Intelligence Summary"
    new_content: str,
    email: str = "vrijen@mycareerspan.com"
) -> bool:
    """
    Prepend intel to a Notion field using read-modify-write.
    
    1. use_app_notion("notion-retrieve-page", pageId=notion_page_id)
    2. Extract current field value
    3. Prepend new_content with timestamp separator
    4. use_app_notion("notion-update-page", pageId=..., propertyValues=[...])
    """
    # This needs to be executed by Zo since it uses app tools
    pass
```

**Format for prepended intel:**
```
---
## [2026-01-18] Meeting: Tope Awotona Sync
**Source:** Meeting B37 block
**Stage:** engaged → negotiating

### Key Facts
- Confirmed interest in partnership
- Budget approved by board
- Timeline: Q1 2026

### Next Action
Schedule follow-up to discuss terms

---
[Previous content below]
```

### Test
```bash
# Retrieve current Notes field
use_app_notion("notion-retrieve-page", {"pageId": "2e85c3d6-a5db-806f-974f-e4e30839c707"})

# Update with prepended content
use_app_notion("notion-update-page", {
    "pageId": "2e85c3d6-a5db-806f-974f-e4e30839c707",
    "propertyValues": [{
        "propertyIdOrName": "Notes",
        "propertyValue": "[NEW CONTENT]\n\n---\n\n[EXISTING CONTENT]"
    }]
})
```

---

## Task 2: SMS Commands Documentation

### Current Capability
The SMS handler (`sms_deal_handler.py`) currently supports **UPDATE ONLY**:

```
n5 deal <company> <update message>
n5 deal "company name" <update message>
```

### What It Does
1. Matches `<company>` to existing deal in `deals.db`
2. Extracts signal (stage change, sentiment, next action) via LLM
3. Updates `deals.db` with new stage/activity
4. Queues Notion sync
5. Returns confirmation SMS

### What It CANNOT Do (Yet)
- ❌ Add new deals
- ❌ Add new contacts
- ❌ Query deal status
- ❌ List deals

### Proposed Extensions

**Add `n5 deal add` command:**
```
n5 deal add <company> <pipeline> [notes]
n5 deal add "Acme Corp" careerspan "Met at conference"
n5 deal add "Cool Startup" zo "Potential data partner"
```

**Add `n5 deal status` command:**
```
n5 deal status darwinbox
→ "Darwinbox: engaged (warm). Last: Meeting 2026-01-15. Next: Send proposal"
```

**Add `n5 deal list` command:**
```
n5 deal list hot
→ "Hot deals: Darwinbox (negotiating), Ribbon (qualified)"
```

### Implementation Location
Extend `parse_sms_deal_command()` and `handle_deal_sms()` in `N5/scripts/sms_deal_handler.py`

---

## Task 3: B37 Block Template

### Template Location
The B37 generator is in `file 'N5/scripts/meeting_deal_intel.py'`

### Current Template Structure

```markdown
---
created: {date}
last_edited: {date}
version: 1.0
provenance: meeting_deal_intel.py
block_type: B37
deal_id: {deal_id}
pipeline: {pipeline}
---

# B37: Deal Intelligence — {company}

## Meeting Context
- **Date:** {meeting_date}
- **Attendees:** {attendees}
- **Meeting Type:** {meeting_type}
- **Deal Type:** {deal_type}
- **Pipeline:** {pipeline}

## Signal Analysis
- **Stage Before:** {stage_before}
- **Stage After:** {stage_after}
- **Confidence:** {confidence}%
- **Sentiment:** {sentiment}
- **Urgency:** {urgency}

## Key Intelligence Extracted

### From B01 (Strategic Recap)
{b01_intel}

### Key Facts
{key_facts_list}

## Recommended Actions
{next_actions}

## Raw Signal Data
```json
{raw_signal_json}
```
```

### Generate Sample B37 for Tope Meeting

**Meeting Path:** `Personal/Meetings/Week-of-2026-01-12/2026-01-16_2026-01-16-Tope-awotona-x-vrijen/`

**Command:**
```bash
cd /home/workspace/N5/scripts
python3 meeting_deal_intel.py --meeting "2026-01-16_2026-01-16-Tope-awotona-x-vrijen" --force
```

**Note:** A B37 already exists at this path. Use `--force` to regenerate with latest template.

---

## Task 4: Email Backfill Strategy

### Current State
- Daily scan runs at 7 AM via scheduled agent
- Scans last 7 days by default
- Tracks processed emails in `processed_emails` table

### Backfill Options

**Option A: Incremental Backfill (Recommended)**
```bash
# Backfill in 30-day chunks to avoid rate limits
python3 N5/scripts/email_deal_scanner.py --days 30 --offset 0   # Last 30 days
python3 N5/scripts/email_deal_scanner.py --days 30 --offset 30  # 30-60 days ago
python3 N5/scripts/email_deal_scanner.py --days 30 --offset 60  # 60-90 days ago
```

**Option B: Contact-Focused Backfill**
```bash
# Only scan emails from/to known deal contacts
python3 N5/scripts/email_deal_scanner.py --scan-contacts --days 90
```

**Option C: Hot Deals Only**
```bash
# Only scan for hot/warm deals
python3 N5/scripts/email_deal_scanner.py --temp hot,warm --days 90
```

### Implementation Needed

Add to `email_deal_scanner.py`:
1. `--offset N` flag to skip first N days
2. `--batch-size N` flag to limit emails per run
3. Rate limiting (Gmail API: 250 quota units/second)
4. Progress tracking (store last processed date)

### Backfill Scheduled Agent

```python
# Create agent for gradual backfill (runs nightly for 2 weeks)
create_agent(
    rrule="FREQ=DAILY;BYHOUR=2;BYMINUTE=0;COUNT=14",
    instruction="""
    Run email backfill for deal intelligence.
    
    1. Check N5/data/backfill_state.json for current offset
    2. Run: python3 N5/scripts/email_deal_scanner.py --days 30 --offset {offset}
    3. Increment offset by 30, save to backfill_state.json
    4. Stop when offset > 180 (6 months)
    """
)
```

---

## Task 5: Checklist

- [ ] **Notion Workaround**: Implement read-modify-write prepend in `notion_deal_sync.py`
- [ ] **Test Notion Prepend**: Update Darwinbox Notes field with test intel
- [ ] **SMS Add Command**: Extend `sms_deal_handler.py` with `n5 deal add`
- [ ] **SMS Status Command**: Add `n5 deal status <company>`
- [ ] **B37 Regenerate**: Force-regenerate B37 for Tope meeting
- [ ] **Email Backfill**: Add `--offset` and `--batch-size` flags
- [ ] **Backfill Agent**: Create scheduled agent for gradual backfill
- [ ] **Documentation**: Update ORCHESTRATOR.md with new commands

---

## Reference Files

**Core Scripts:**
- `file 'N5/scripts/deal_signal_router.py'` — Signal routing core
- `file 'N5/scripts/sms_deal_handler.py'` — SMS command parser
- `file 'N5/scripts/meeting_deal_intel.py'` — B37 generator
- `file 'N5/scripts/email_deal_scanner.py'` — Gmail scanner
- `file 'N5/scripts/notion_deal_sync.py'` — Notion sync

**Config:**
- `file 'N5/config/notion_field_mapping.json'` — Notion field IDs
- `file 'N5/config/deal_signal_config.json'` — Stage definitions

**Build Docs:**
- `file 'N5/builds/deal-meeting-intel/STATUS.md'` — Full build status
- `file 'N5/builds/deal-meeting-intel/ORCHESTRATOR.md'` — System overview
- `file 'N5/builds/deal-meeting-intel/DESIGN.md'` — Architecture

**Database:**
- `file 'N5/data/deals.db'` — 77 deals, 32 contacts

**Tope Meeting:**
- `file 'Personal/Meetings/Week-of-2026-01-12/2026-01-16_2026-01-16-Tope-awotona-x-vrijen/'`

---

## How to Start

1. Read this file for full context
2. Start with Task 1 (Notion workaround) — test on Darwinbox page
3. Then Task 3 (B37 regeneration) — quick win
4. Then Task 2 (SMS extensions) — new commands
5. Finally Task 4 (email backfill) — scheduled agent

**Notion Test Page:**
- Company: Darwinbox
- Page ID: `2e85c3d6-a5db-806f-974f-e4e30839c707`
- URL: https://www.notion.so/Darwinbox-2e85c3d6a5db806f974fe4e30839c707
