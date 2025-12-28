---
created: 2025-12-27
last_edited: 2025-12-27
version: 1
provenance: con_uvuYqpsPTqWJCJOM
---
# Airtable Schema Update Required

## Deals Table (`tblVvlBtY4QtmA7ss`)

Add these fields manually in Airtable:

| Field Name | Field Type | Options/Notes |
|------------|------------|---------------|
| Last Meeting Date | Single Line Text | Format: YYYY-MM-DD |
| Meeting Count | Number | Integer, precision 0 |
| Momentum | Single Select | Options: Accelerating, Steady, Stalling, Stalled |
| Deal Health | Single Select | Options: 🟢 Healthy, 🟡 Needs Attention, 🔴 At Risk |
| Next Steps | Long Text | Append-only: what should happen next |
| Open Action Items | Long Text | Uncompleted commitments from meetings |
| Blockers | Long Text | Risks and obstacles preventing progress |

## Why Manual?

The Airtable API's `create-field` endpoint requires specific permissions that may not be enabled for this integration. These fields can be added in ~2 minutes via the Airtable UI.

## After Adding Fields

Run this to verify the schema:
```bash
python3 N5/scripts/airtable_schema_check.py
```

Then the context-aware sync will work automatically.

