---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_1xhFJwHkZOZPZ38m
---

# Deal System Consolidation — 2026-01-19

## Summary

Consolidated the intro-leads subsystem into the main deal database. All broker/intro signals now route through `deal_proactive_sensor.py` which:
- Detects broker patterns in text
- Queues for V's SMS approval
- Creates `deal_contacts` entries on approval

## Changes Made

### 1. Modified `N5/scripts/zth_spawn_worker.py`

**Before:** `execute_intro_lead()` wrote to `N5/lists/intro-leads.jsonl` — a dead-end file with no downstream processing.

**After:** `execute_intro_lead()` now:
1. Constructs broker signal text from ZTH entry parameters
2. Calls `deal_proactive_sensor.py --text "<signal>" --source meeting`
3. Sensor handles approval flow + database insertion

### 2. Deprecated Files

- `N5/lists/intro-leads.jsonl` → `N5/lists/intro-leads.jsonl.DEPRECATED`
- `Lists/intro-leads.jsonl` → `Lists/intro-leads.jsonl.DEPRECATED`

### 3. Data Flow (New)

```
Meeting → B00_ZO_TAKE_HEED.jsonl
    ↓ (task_type: intro_lead)
zth_spawn_worker.py → execute_intro_lead()
    ↓ (constructs broker signal text)
deal_proactive_sensor.py
    ↓ (detects entity, queues approval)
SMS to V: "New broker contact detected..."
    ↓ (V replies "Y")
deal_contacts table in deals.db
```

## System Architecture

See: `file 'Images/deal-system-v2-consolidated_1.png'`

## Key Scripts

| Script | Role |
|--------|------|
| `N5/scripts/zth_spawn_worker.py` | Processes B00 ZTH entries, routes intro_lead to sensor |
| `N5/scripts/deal_proactive_sensor.py` | Central signal processing, approval flow, DB writes |
| `N5/scripts/sms_deal_handler.py` | SMS interface for deal commands |
| `N5/scripts/deal_cli.py` | CLI for deal queries |

## Validation

Tested with simulated ZTH entry:
```python
entry = {
    'task_type': 'intro_lead',
    'additional_params': {
        'source_person': 'Mike Chen',
        'target_person': 'Lisa Wang',
        'target_company': 'Stripe',
        'target_role': 'Head of Partnerships',
        'context': 'Mike offered to intro during coffee chat'
    }
}
```

Result: Successfully routed to deal_proactive_sensor, generated SMS approval request.

## Current Deal Stats

| Metric | Count |
|--------|-------|
| Total deals | 99 |
| Zo partnerships | 25 |
| Careerspan acquirers | 53 |
| Leadership contacts | 21 |
| Deal contacts | 33 |
| Deal activities | 50 |
