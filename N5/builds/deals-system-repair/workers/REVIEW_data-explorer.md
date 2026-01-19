---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_ZGBnCCZnbKMYnfcF
worker_id: REVIEW
---

# Worker Brief: Data Review & Query Session

**Pre-decided thread title:** `[deals-system-repair] REVIEW: Data Explorer`

## Purpose
Interactive session for V to review and query the deals system repair results. Flexible exploration of deals, meeting classifications, and linkages.

## Context: What Was Done

### Build Summary
The `deals-system-repair` build fixed and consolidated the deals system:

1. **Script Fix** — `deal_sync_external.py` had orphan code causing syntax error (fixed)
2. **Data Sync** — 98 deals now in DB (25 zo_partnership, 51 careerspan_acquirer, 22 leadership)
3. **External Source Backfill** — All 98 deals now have `external_source` field populated
4. **Leadership Type Fix** — 21 records were mis-typed as `careerspan_acquirer`, now correctly `leadership`
5. **Meeting Routing** — 153 meetings classified with dual-lens scoring (Zo relevance + Careerspan relevance)
6. **Deal Linkage** — 50 deal_activities created linking meetings to deals
7. **Agent Consolidation** — Deleted redundant agent `259a13c8`

### Key Files & Locations

| Asset | Location |
|-------|----------|
| Deals database | `/home/workspace/N5/data/deals.db` |
| Routing results | `/home/workspace/N5/cache/deal_sync/routing_results.jsonl` |
| B36 files (per-meeting) | `Personal/Meetings/<week>/<meeting>/B36_DEAL_ROUTING.json` |
| Build documentation | `N5/builds/deals-system-repair/` |
| Worker completions | `N5/builds/deals-system-repair/completions/` |

### Database Schema (Key Tables)

**deals**
- `id`, `deal_type`, `company`, `stage`, `temperature`, `external_source`, `owner`, `metadata_json`

**deal_activities**
- `id`, `deal_id`, `activity_type`, `activity_date`, `source_meeting`, `notes`

**deal_contacts**
- `id`, `deal_id`, `contact_name`, `contact_role`, `linkedin_url`

## Ready Queries

### Deals Overview
```bash
python3 /home/workspace/N5/scripts/deal_cli.py summary
python3 /home/workspace/N5/scripts/deal_cli.py list --type zo_partnership
python3 /home/workspace/N5/scripts/deal_cli.py list --type leadership
python3 /home/workspace/N5/scripts/deal_cli.py list --type careerspan_acquirer
```

### Direct SQL Queries
```bash
# All deals with their activity counts
sqlite3 /home/workspace/N5/data/deals.db "
SELECT d.id, d.company, d.deal_type, COUNT(a.id) as activities
FROM deals d
LEFT JOIN deal_activities a ON d.id = a.deal_id
GROUP BY d.id ORDER BY activities DESC LIMIT 20;"

# Recent deal activities
sqlite3 /home/workspace/N5/data/deals.db "
SELECT deal_id, activity_type, activity_date, source_meeting
FROM deal_activities ORDER BY activity_date DESC LIMIT 20;"

# Deals by external source
sqlite3 /home/workspace/N5/data/deals.db "
SELECT external_source, COUNT(*) FROM deals GROUP BY external_source;"
```

### Meeting Routing Results
```bash
# Count of routed meetings by relevance
python3 -c "
import json
zo_high = cs_high = both = neither = 0
with open('/home/workspace/N5/cache/deal_sync/routing_results.jsonl') as f:
    for line in f:
        r = json.loads(line)
        zo = r.get('zo_relevance_score', 0)
        cs = r.get('careerspan_relevance_score', 0)
        if zo >= 0.7 and cs >= 0.7: both += 1
        elif zo >= 0.7: zo_high += 1
        elif cs >= 0.7: cs_high += 1
        else: neither += 1
print(f'Zo high: {zo_high}, CS high: {cs_high}, Both: {both}, Neither: {neither}')
"

# Sample a specific meeting's routing
cat /home/workspace/Personal/Meetings/Week-of-2026-01-12/2026-01-14_2026-01-14-V-logan-acquisition-strategy-201734/B36_DEAL_ROUTING.json | python3 -m json.tool
```

### Find Specific Data
```bash
# Search deals by company name
sqlite3 /home/workspace/N5/data/deals.db "SELECT * FROM deals WHERE company LIKE '%calendly%';"

# Find meetings linked to a deal
sqlite3 /home/workspace/N5/data/deals.db "SELECT * FROM deal_activities WHERE deal_id LIKE '%calendly%';"

# Find high-relevance meetings
python3 -c "
import json
with open('/home/workspace/N5/cache/deal_sync/routing_results.jsonl') as f:
    for line in f:
        r = json.loads(line)
        if r.get('zo_relevance_score', 0) >= 0.8:
            print(f\"{r['meeting_name']}: Zo={r['zo_relevance_score']:.2f}, CS={r.get('careerspan_relevance_score',0):.2f}\")
"
```

## Your Role
1. Answer V's questions about the data flexibly
2. Run queries as needed — adapt the examples above
3. If V finds issues (wrong classifications, missing links, bad data), note them clearly
4. **Do NOT fix issues in this thread** — just document them
5. At the end, if there are issues, tell V to return to the orchestrator thread (con_ZGBnCCZnbKMYnfcF)

## Issues to Report Back
If V identifies problems, collect them in this format:
```
ISSUES FOR ORCHESTRATOR:
1. [Issue description] — [specific example]
2. ...
```

V will paste this back into the orchestrator thread for a fix wave if needed.

## Constraints
- This is a READ-ONLY exploration session
- Do NOT modify the database
- Do NOT modify any files
- Do NOT commit anything
- Just query, explore, and document issues
