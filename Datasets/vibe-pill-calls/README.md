---
created: 2026-02-20
last_edited: 2026-02-20
version: 1.0
provenance: con_U9bz2q9Ilujko18W
---

# Vibe Pill Hotline — Call Analytics Dataset

Call analytics, member identity, and application funnel tracking for The Vibe Pill membership hotline.

## Overview

Unlike the Zo Hotline (anonymous advisory), this dataset includes **member identity resolution** — callers are matched to member profiles for personalized service, engagement tracking, and membership funnel analytics.

## Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| **calls** | Per-call records with member context | id, member_phone, pathway, outcome, summary |
| **member_profiles** | Persistent member identity + engagement | phone (PK), name, status, tier, total_calls |
| **applications** | Membership application pipeline | id, phone, status, screening_notes |
| **escalations** | V follow-up requests | id, call_id, name, contact, reason |
| **feedback** | Post-call satisfaction | id, call_id, satisfaction, comment |
| **daily_analysis** | LLM-generated daily analytics | analysis_date, patterns_json, improvements_json |

## Quick Start

```bash
# Check tables
duckdb Datasets/vibe-pill-calls/data.duckdb -c "SHOW TABLES"

# Member engagement
duckdb Datasets/vibe-pill-calls/data.duckdb -c "
  SELECT name, tier, total_calls, last_call_at
  FROM member_profiles
  WHERE status = 'member'
  ORDER BY total_calls DESC
  LIMIT 10
"

# Application funnel
duckdb Datasets/vibe-pill-calls/data.duckdb -c "
  SELECT status, COUNT(*) as count
  FROM applications
  GROUP BY status
"

# Calls by pathway
duckdb Datasets/vibe-pill-calls/data.duckdb -c "
  SELECT pathway, COUNT(*) as calls, AVG(duration_seconds) as avg_dur
  FROM calls
  GROUP BY pathway
  ORDER BY calls DESC
"
```

## Ingest

The ingest script accepts VAPI webhook payloads and secondary operations:

```bash
# Ingest a VAPI call payload
python3 ingest/ingest.py --file payload.json

# Dry run (parse + validate, no writes)
python3 ingest/ingest.py --file payload.json --dry-run

# Upsert a member profile
python3 ingest/ingest.py --upsert-member '{"phone":"+18575551234","name":"David Chen","status":"member","tier":"founding-15"}'

# Log an escalation
python3 ingest/ingest.py --log-escalation '{"call_id":"call_abc","name":"David","contact":"david@ex.com","reason":"Cobuild request"}'

# Log feedback
python3 ingest/ingest.py --log-feedback '{"call_id":"call_abc","caller_name":"David","satisfaction":5,"comment":"Great session"}'

# Log a new application
python3 ingest/ingest.py --log-application '{"phone":"+18575551234","name":"Sarah Kim","screening_notes":"Strong fit"}'
```

## Data Flow

1. VAPI webhook fires on call end → webhook handler calls `ingest.py --payload`
2. Ingest resolves caller identity via `member_profiles` lookup
3. Call record written with member context (name, status)
4. Member profile stats updated (total_calls, last_call_at)
5. Tool calls during conversation trigger escalation/feedback/application writes
6. Daily analysis agent aggregates patterns across calls and feedback

## Schema Details

See `schema.yaml` for full column definitions, types, allowed values, and example queries.
