---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# CRM V3 – Unified Relationship Intelligence

```yaml
capability_id: crm-v3
name: "CRM V3 – Unified Relationship Intelligence System"
category: internal
status: active
confidence: high
last_verified: 2025-11-29
tags:
  - crm
  - relationships
  - intelligence
  - enrichment
entry_points:
  - type: script
    id: "N5/scripts/crm_cli.py"
  - type: script
    id: "N5/crm_v3/enrichment/enrichment_worker.py"
  - type: script
    id: "N5/scripts/crm_calendar_webhook.py"
  - type: script
    id: "N5/scripts/crm_email_tracker.py"
owner: "V"
```

## What This Does

CRM V3 is the central system for storing, enriching, and querying relationship intelligence. It unifies data from calendar, email, LinkedIn, Aviato and internal systems into YAML profile files plus a SQLite database, giving Zo agents a single place to understand who someone is, how strong the relationship is, and what actions to take next.

It owns the **profiles corpus**, the **enrichment queue**, and the **intelligence_sources** registry that keeps attribution and quality metadata for all imported signals.

## How to Use It

### CLI entry points

Run from `/home/workspace`:

```bash
# Stats and basic visibility
python3 N5/scripts/crm_cli.py stats
python3 N5/scripts/crm_cli.py list

# Search
python3 N5/scripts/crm_cli.py search --name "Jane"
python3 N5/scripts/crm_cli.py search --email "jane@example.com"

# Create a profile
python3 N5/scripts/crm_cli.py create \
  --name "Jane Doe" \
  --email "jane@example.com" \
  --category NETWORKING

# View intelligence
python3 N5/scripts/crm_cli.py intel jane_doe

# Enrich a specific profile
python3 N5/scripts/crm_cli.py enrich jane_doe
```

### Enrichment worker

```bash
# Process all queued enrichment jobs
python3 N5/crm_v3/enrichment/enrichment_worker.py

# Quick validation
sqlite3 N5/data/crm_v3.db "SELECT status, COUNT(*) FROM enrichment_queue GROUP BY status"
```

In production, this worker is intended to run on a **6‑hour cadence** via a Zo scheduled task and will gradually enrich profiles using Gmail, Aviato, LinkedIn and calendar signals as those integrations come online.

## Associated Files & Assets

### Data & schema

- `file 'N5/crm_v3/profiles/'` – YAML profile SSOT directory.
- `file 'N5/data/crm_v3.db'` – SQLite database for fast queries and enrichment queues.
- `file 'N5/crm_v3/db/schema.sql'` – Canonical database schema.

### Implementation & orchestration

- `file 'N5/crm_v3/README.md'` – Primary system guide and operational documentation.
- `file 'N5/orchestration/crm-v3-unified/ORCHESTRATOR_MONITOR.md'` – Multi-worker build and validation log.
- `file 'N5/scripts/crm_cli.py'` – CLI entry point for all core operations.
- `file 'N5/crm_v3/enrichment/enrichment_worker.py'` – Tool-first enrichment worker.
- `file 'N5/crm_v3/enrichment/gmail_analyzer.py'` – Gmail thread analysis (stubbed for Zo tools).
- `file 'N5/crm_v3/enrichment/aviato_enricher.py'` – External context enrichment stub.
- `file 'N5/crm_v3/enrichment/linkedin_scraper.py'` – LinkedIn enrichment stub.

### Tables (selected)

- **profiles** – Core profile rows: email, name, yaml_path, category, relationship_strength, enrichment_status, meeting_count, intelligence_block_count, search_text.
- **enrichment_queue** – Jobs to run: profile_id, priority, scheduled_for, checkpoint, status, attempt_count, error_message.
- **intelligence_sources** – Source‑level attribution and confidence per profile.
- **calendar_events / event_attendees** – Calendar‑driven profile creation and meeting statistics.

## Workflow

### Data flow overview

```mermaid
flowchart TD
  A[Signals
  - Calendar events
  - Gmail threads
  - Aviato/LinkedIn
  - Manual entries] --> B[profiles YAML
  + crm_v3.db.profiles]

  B --> C[enrichment_queue
  (prioritized jobs)]
  C --> D[enrichment_worker.py
  - tool-first enrichment]
  D --> E[intelligence_sources
  + YAML Intelligence Log]
  E --> F[Zo agents & CLIs
  - intel, search, next actions]
```

### Typical lifecycle

1. **Profile creation**  
   - Automatic, from calendar events (future) or ingestion scripts.  
   - Manual via `crm_cli.py create`.

2. **Queue enrichment**  
   - New or stale profiles inserted into `enrichment_queue` with priority based on category (e.g. INVESTOR > NETWORKING).

3. **Run enrichment worker**  
   - For each job, the worker calls into Zo tools (Gmail / LinkedIn / Aviato / calendar) to assemble context, then appends an "Intelligence Log" entry into the profile’s YAML and records source rows.

4. **Query & usage**  
   - `crm_cli.py intel <slug>` renders a rich view of meetings, threads, and prior notes.  
   - Other systems (e.g. meeting pipeline, content library) can query `crm_v3.db` for relationship‑aware behavior.

## Notes / Gotchas

- **YAML is the SSOT.** The database exists for performance and search convenience; do not treat it as the canonical record without cross‑checking the YAML file.
- **External APIs are stubbed.** Until Gmail/LinkedIn/Aviato integrations are wired via Zo’s `use_app_*` tools, enrichment jobs will run in a partial/stubbed mode. Treat status values accordingly.
- **Migration scripts exist.** Legacy CRM data is migrated via `crm_migrate_to_v3.py` (see orchestrator monitor); re‑running migrations without care can create duplicates.
- **Search depends on search_text.** If CLI search behaves oddly, re-run the architectural validation / integration tests before assuming data loss.

