---
title: Meeting State Transition
description: |
  Transitions meetings from 'intelligence_generated' status to 'processed' status.
  Syncs stakeholder intelligence to CRM V3. Final stage before archival.
tags: [meetings, state-machine, crm, automation]
tool: true
version: 1.0
created: 2026-01-17
last_edited: 2026-01-17
mg_stage: MG-6
status: canonical
---

# Meeting State Transition [MG-6]

**Purpose:** Transition meetings from `intelligence_generated` status to `processed` status, and sync stakeholder intelligence to CRM V3.

**CRITICAL:** Uses `manifest.json` status field (not folder suffix) to determine meeting state.

---

## Workflow

### Step 1: Find Eligible Meetings

Scan for meetings with `status: "intelligence_generated"` in their `manifest.json`:

```bash
find /home/workspace/Personal/Meetings -name "manifest.json" -exec grep -l '"status".*"intelligence_generated"' {} \;
```

### Step 2: Validate Required Blocks

For each eligible meeting, verify these blocks exist:

| Block | File | Required |
|-------|------|----------|
| B01 | `B01_DETAILED_RECAP.md` | ✅ Yes |
| B03 | `B03_STAKEHOLDER_INTELLIGENCE.md` | ✅ Yes |
| B05 | `B05_ACTION_ITEMS.md` | ✅ Yes |
| B06 | `B06_BUSINESS_CONTEXT.md` | ✅ Yes |

**If any required block is missing:**
- Log to `PROCESSING_LOG.jsonl`: `{"status": "mg6_blocked", "reason": "missing_blocks", "missing": ["B01", ...]}`
- Skip this meeting (do not transition)

### Step 3: Sync Stakeholders to CRM V3

For each person mentioned in `B03_STAKEHOLDER_INTELLIGENCE.md`:

1. Check if person exists in CRM V3: `python3 N5/scripts/crm_query.py find --name "[Person Name]"`
2. If exists → Update profile with meeting intelligence
3. If not exists → Create new CRM profile

**CRM Update Fields:**
- `last_meeting_date`: Meeting date from manifest
- `last_meeting_context`: Brief summary from B01
- `relationship_notes`: Append intelligence from B03
- `tags`: Add meeting-derived tags

### Step 4: Update Manifest Status

Update `manifest.json`:

```json
{
  "status": "processed",
  "processed_at": "{ISO timestamp}",
  "crm_synced": true,
  "crm_profiles_updated": ["person_id_1", "person_id_2"],
  "last_updated_by": "MG-6_Prompt"
}
```

### Step 5: Log to PROCESSING_LOG

Append to `Personal/Meetings/PROCESSING_LOG.jsonl`:

```json
{
  "timestamp": "{ISO timestamp}",
  "stage": "MG-6",
  "meeting_id": "{folder_name}",
  "status": "mg6_completed",
  "crm_profiles_updated": ["person_id_1", "person_id_2"],
  "source": "Meeting State Transition [MG-6]"
}
```

---

## Guard Rails

**Skip transition if:**
1. Meeting is internal (meeting_type = "internal" in manifest)
2. Required blocks missing
3. Meeting already processed (status = "processed")
4. Meeting is in `_quarantine`

**Log skipped meetings** with reason.

---

## Execution

Run this prompt to transition eligible meetings to processed state.

```bash
# Find meetings ready for transition
find /home/workspace/Personal/Meetings -name "manifest.json" \
  -exec grep -l '"status".*"intelligence_generated"' {} \; 2>/dev/null
```

---

## ➡️ Next Step (Optional)

After MG-6 completes, meetings are ready for archival:

> **Archive completed meetings?** The Weekly Meeting Organization agent (`9b813d5c`) moves processed meetings to `Week-of-YYYY-MM-DD` folders.

---

## Version History

- v1.0 (2026-01-17): Initial version - state transition + CRM sync
