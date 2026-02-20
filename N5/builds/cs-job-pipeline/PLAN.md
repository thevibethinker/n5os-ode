---
created: 2026-02-19
last_edited: 2026-02-19
version: 1.1
type: build_plan
status: in_progress
---

# Plan: Careerspan Job Sourcing Pipeline

**Objective:** Build a prompt-driven job sourcing system that uses SourceStack to discover, classify, age, and curate software engineering jobs across three geography tiers, with a self-improving archetype system for role matching and a 30/60/90-day lifecycle for job freshness.

**Trigger:** V wants a systematic way to surface engineering jobs for Careerspan clients — both targeted (company watchlist) and broad (role-based sweeps) — with human-in-the-loop approval before jobs reach the Notion "Job board" database.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [x] All questions resolved via two rounds of clarification

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    V (via prompting)                     │
│   "show me today's NYC jobs" / "approve these 5"        │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              sourcestack.py (enhanced CLI)               │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐    │
│  │ Watchlist │  │ Role     │  │ Archetype Engine   │    │
│  │ Scan     │  │ Sweep    │  │ (title taxonomy)   │    │
│  │ (daily)  │  │ (3-4 day)│  │                    │    │
│  └────┬─────┘  └────┬─────┘  └────────┬───────────┘    │
│       │              │                 │                 │
│       └──────┬───────┘                 │                 │
│              ▼                         │                 │
│  ┌───────────────────────┐             │                 │
│  │  Geo-List Router      │◄────────────┘                 │
│  │  NYC │ US-Remote │ Intl│                              │
│  └───────────┬───────────┘                               │
│              ▼                                           │
│  ┌───────────────────────┐                               │
│  │  SQLite (sourcestack  │                               │
│  │  .db) + freshness     │                               │
│  │  scoring + lifecycle  │                               │
│  └───────────┬───────────┘                               │
│              │                                           │
│  ┌───────────▼───────────┐     ┌───────────────────┐    │
│  │  Approval Queue       │────►│  Notion Sync      │    │
│  │  (status: pending →   │     │  (push approved,  │    │
│  │   approved/rejected)  │     │   prune stale)    │    │
│  └───────────────────────┘     └───────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingest**: SourceStack API → normalize → SQLite (with geo-list tag, freshness score, archetype tag)
2. **Review**: V prompts Zo → query SQLite → display candidates → V approves/rejects
3. **Publish**: Approved jobs → Notion "Job board" DB (with Type: "Direct Apply" or "Source Job")
4. **Lifecycle**: Weekly pruner → 30d close → 60d delete local → 90d expunge Notion

### Three Geography Lists

| List | SourceStack Filter | Description |
|------|-------------------|-------------|
| `nyc` | `city` IN ["New York", "Brooklyn", "Manhattan", ...] AND `country` = "United States" | NYC metro only |
| `us-remote` | `country` = "United States" AND (`remote` = True OR `city` contains key US cities) | US-based, remote-friendly |
| `intl-remote` | `remote` = True AND `country` != "United States" | International remote-accepting |

### Archetype System

Archetypes are YAML-defined role categories. Each archetype has:
- A canonical name (e.g., `backend-engineer`)
- A list of title patterns that map to it
- A SourceStack `categories` filter for double-check

```yaml
archetypes:
  backend-engineer:
    titles:
      - backend engineer
      - backend developer
      - server engineer
      - API engineer
    categories: [Engineering, Software Development]
  
  frontend-engineer:
    titles:
      - frontend engineer
      - frontend developer
      - UI engineer
      - react developer
    categories: [Engineering, Software Development]
  
  # ... more archetypes
```

When querying, archetypes string their titles together into a single `CONTAINS_ANY` filter, maximizing signal per API call.

The archetype file is designed to grow over time — V or Zo can add new titles based on observation.

### Job Lifecycle (Freshness Tiers)

| Age | Status | Local DB Action | Notion Action |
|-----|--------|-----------------|---------------|
| 0-14d | `fresh` | Active | Active |
| 15-29d | `aging` | Active (flagged) | Active (flagged) |
| 30d | `stale` | Auto-close | Remove from Notion |
| 60d | `expired` | Delete from local DB | — |
| 90d | — | — | Hard expunge any remnants |

Freshness score = `days_since_first_indexed / 30` (percentage of 30-day window).

### Credit Budget

- Daily cap: 500 credits
- Watchlist scan: daily (~5-20 credits)
- Role-based sweep: every 3-4 days (~100-300 credits)
- Credit tracking in `scans` table

---

## Checklist

### Phase 1: Core Infrastructure
- ☑ Create archetype YAML config with initial role taxonomy
- ☑ Upgrade SQLite schema (geo_list, archetype, freshness_score, approval_status, notion_page_id, job_type)
- ☑ Add credit cap enforcement to API layer
- ☑ Add freshness scoring function
- ☑ Test: Schema migration on existing DB, freshness calc, credit cap

### Phase 2: Query Engine
- ☑ Implement geo-list routing (NYC / US-Remote / Intl-Remote filters)
- ☑ Implement archetype-based search (string titles into CONTAINS_ANY)
- ☑ Add `sweep` command (role-based broad search across all companies)
- ☑ Add `review` command (show pending jobs, support approve/reject)
- ☑ Test: Live queries against SourceStack, verify geo classification

### Phase 3: Notion Sync
- ☐ Build Notion push module (approved jobs → Job board DB)
- ☐ Map fields: Name, Job title (rich_text), Company (rich_text), Comp, Location, Setup, Type
- ☐ Build Notion prune module (remove stale jobs by notion_page_id)
- ☐ Switch Job title and Company to rich_text in Notion schema
- ☐ Test: Push a test job, verify Notion fields, prune a stale job

### Phase 4: Pruning Agent + Lifecycle
- ☑ Implement lifecycle state machine (fresh → aging → stale → expired → expunged)
- ☑ Build `prune` CLI command (can be run manually or by agent)
- ☐ Create weekly scheduled agent for pruning
- ☑ Test: Lifecycle command works with dry-run

---

## Phase 1: Core Infrastructure

### Affected Files
- `Skills/sourcestack-monitor/assets/archetypes.yaml` - CREATE - Role taxonomy config
- `Skills/sourcestack-monitor/scripts/sourcestack.py` - UPDATE - Schema upgrade, credit cap, freshness
- `Skills/sourcestack-monitor/data/sourcestack.db` - UPDATE - Schema migration

### Changes

**1.1 Archetype YAML Config:**
Create `assets/archetypes.yaml` with initial taxonomy:
- `backend-engineer` (backend, server, API, systems)
- `frontend-engineer` (frontend, UI, react, vue, angular)
- `fullstack-engineer` (full-stack, fullstack)
- `founding-engineer` (founding)
- `staff-engineer` (staff, principal)
- `sre-platform` (SRE, platform, infrastructure, DevOps, cloud)
- `data-engineer` (data engineer, ETL, data platform)
- `ml-engineer` (ML, machine learning, AI engineer)
- `mobile-engineer` (iOS, Android, mobile, React Native, Flutter)
- `security-engineer` (security, AppSec, InfoSec)

Each archetype includes `categories` filter (default: `[Engineering, Software Development]`).

**1.2 SQLite Schema Upgrade:**
Add columns to `jobs` table:
- `geo_list TEXT` — one of: `nyc`, `us-remote`, `intl-remote`, `unclassified`
- `archetype TEXT` — which archetype matched this job
- `freshness_score REAL` — days_since_first_indexed / 30
- `approval_status TEXT DEFAULT 'pending'` — `pending`, `approved`, `rejected`
- `job_type TEXT` — `direct_apply` or `source_job`
- `notion_page_id TEXT` — Notion page ID after sync
- `approved_at TEXT` — timestamp of approval
- `pruned_at TEXT` — timestamp of removal from Notion

Add migration logic that preserves existing data.

**1.3 Credit Cap Enforcement:**
Add to `post_to_api()`:
- Track daily credit usage in a new `credit_log` table
- Before each API call, check `SUM(credits) WHERE date = today`
- If approaching 500 cap, warn and stop
- New CLI: `sourcestack.py credits` — show today's usage and remaining budget

**1.4 Freshness Scoring:**
Add function `compute_freshness(first_indexed: str) -> dict`:
- Returns `{days: int, score: float, tier: str}`
- Tier mapping: 0-14d → "fresh", 15-29d → "aging", 30+d → "stale"
- Score = days / 30 (0.0 = brand new, 1.0 = 30 days, >1.0 = overdue)

### Unit Tests
- Schema migration preserves existing Stripe test data: verify row count unchanged
- `compute_freshness("2026-02-19")` → `{days: 0, score: 0.0, tier: "fresh"}`
- `compute_freshness("2026-01-20")` → `{days: 30, score: 1.0, tier: "stale"}`
- Credit cap blocks when daily total ≥ 500

---

## Phase 2: Query Engine

### Affected Files
- `Skills/sourcestack-monitor/scripts/sourcestack.py` - UPDATE - New commands and geo routing
- `Skills/sourcestack-monitor/assets/archetypes.yaml` - READ - Load archetype definitions

### Changes

**2.1 Geo-List Router:**
New function `classify_geo(job: dict) -> str`:
- Check city against NYC metro list → `nyc`
- Check country = US AND (remote=True OR major US city) → `us-remote`
- Check remote=True AND country != US → `intl-remote`
- Else → `unclassified`

Applied during normalization, stored in `geo_list` column.

**2.2 Archetype Search Engine:**
New function `load_archetypes() -> dict` reads `archetypes.yaml`.
New function `build_archetype_query(archetype_names: list, geo: str) -> dict`:
- Collects all titles across requested archetypes
- Strings them into single `CONTAINS_ANY` filter
- Adds `categories` filter as double-check
- Adds geo filters based on target list
- Returns SourceStack API payload

**2.3 New CLI Command — `sweep`:**
```bash
sourcestack.py sweep --geo nyc --archetypes backend-engineer,frontend-engineer --limit 100
sourcestack.py sweep --geo us-remote --all-archetypes --limit 200
sourcestack.py sweep --geo intl-remote --archetypes ml-engineer --limit 50
```
- Runs the role-based broad search (every 3-4 days)
- Results go through geo classifier + archetype tagger + freshness scorer
- All stored in SQLite with `approval_status = 'pending'`

**2.4 New CLI Command — `review`:**
```bash
sourcestack.py review --geo nyc --archetype backend-engineer --fresh-only
sourcestack.py review --pending --limit 20
sourcestack.py review --approve <post_uuid> [<post_uuid> ...]  --type direct_apply
sourcestack.py review --approve <post_uuid> [<post_uuid> ...]  --type source_job
sourcestack.py review --reject <post_uuid> [<post_uuid> ...]
```
- Shows pending jobs in a readable format (company, title, location, freshness, comp)
- Supports batch approve/reject by UUID
- `--type` sets `direct_apply` or `source_job` on approval

### Unit Tests
- Geo classifier: NYC job → `nyc`, SF remote job → `us-remote`, London remote → `intl-remote`
- Archetype query builds correct `CONTAINS_ANY` with all titles from requested archetypes
- `sweep --dry-run` produces valid API payload without calling API
- `review --pending` returns only `approval_status = 'pending'` jobs

---

## Phase 3: Notion Sync

### Affected Files
- `Skills/sourcestack-monitor/scripts/sourcestack.py` - UPDATE - Add notion sync commands
- Notion "Job board" DB (ID: `29c5c3d6-a5db-81a3-9aa6-000b1c83fa24`) - UPDATE - Schema + data

### Changes

**3.1 Notion Push Module:**
New function `push_to_notion(jobs: list[JobRecord]) -> list[str]`:
- For each approved job, create a page in the Notion "Job board" DB
- Field mapping:
  - `Name` (title) → company_name + " — " + job_name
  - `Job title` (rich_text) → job_name
  - `Company` (rich_text) → company_name
  - `Comp` → comp_range
  - `Location` → city + ", " + country
  - `Setup` (select) → map from `remote` field: True → "Remote", else "In-office" or "Hybrid"
  - `Type` (select) → NEW PROPERTY: "Direct Apply" or "Source Job"
  - `Status` (select) → "Active"
  - `URL` (url) → post_url or post_apply_url
- Returns list of created notion_page_ids
- Updates local DB with `notion_page_id` for each pushed job

New CLI command:
```bash
sourcestack.py publish           # push all approved, un-synced jobs to Notion
sourcestack.py publish --dry-run # show what would be pushed
```

**3.2 Notion Prune Module:**
New function `prune_from_notion(stale_jobs: list) -> int`:
- For jobs with `status = 'stale'` AND `notion_page_id IS NOT NULL`
- Archive (not delete) the Notion page
- Update local DB: set `pruned_at` timestamp

New CLI command:
```bash
sourcestack.py notion-prune           # remove stale jobs from Notion
sourcestack.py notion-prune --dry-run
```

**3.3 Notion Schema Changes (last):**
- Switch "Job title" from select → rich_text
- Switch "Company" from select → rich_text  
- Add "Type" select property with options: "Direct Apply", "Source Job"
- Add "URL" url property

NOTE: Notion property type changes require creating new properties and migrating data. The script should handle this gracefully.

### Unit Tests
- Push a single test job → verify Notion page created with correct fields
- Push with dry-run → no Notion API calls made
- Prune a stale job → Notion page archived, local DB updated

---

## Phase 4: Pruning Agent + Lifecycle

### Affected Files
- `Skills/sourcestack-monitor/scripts/sourcestack.py` - UPDATE - Lifecycle commands
- Scheduled agent - CREATE - Weekly pruning

### Changes

**4.1 Lifecycle State Machine:**
New function `run_lifecycle() -> dict`:
- Query all active jobs
- For each, compute freshness
- Apply transitions:
  - `fresh` + 15d+ → update to `aging`
  - `aging` + 30d+ → update to `stale`, auto-close
  - `stale` + 60d+ → update to `expired`, delete from local DB
  - Any job in Notion + 90d+ → expunge from Notion (hard archive)
- Returns stats: `{aged: N, staled: N, expired: N, expunged: N}`

New CLI command:
```bash
sourcestack.py lifecycle           # run full lifecycle pass
sourcestack.py lifecycle --dry-run # preview transitions
```

**4.2 Prune CLI:**
```bash
sourcestack.py prune           # lifecycle + notion prune in one command
sourcestack.py prune --dry-run
```
Combines lifecycle transitions + Notion pruning into single operation.

**4.3 Weekly Scheduled Agent:**
- Name: "⇱ Careerspan Job Pruner"  
- Schedule: Weekly, Sundays at 8 AM ET
- Action: Run `sourcestack.py prune`, email V a summary
- Cornerstone task (⇱ prefix)

### Unit Tests
- Job at 31 days → transitions from aging to stale
- Job at 61 days → deleted from local DB
- Job at 91 days in Notion → expunged
- Dry-run produces correct preview without mutations

---

## Pulse Suitability Assessment

**Verdict: Sequential, NOT Pulse.**

Rationale:
- Phases are highly interdependent (Phase 2 needs Phase 1's schema, Phase 3 needs Phase 2's approval flow)
- Single skill file (`sourcestack.py`) is the primary target — parallel workers editing same file = merge conflicts
- Total scope is ~400-500 lines of new code additions to an existing ~350-line script
- Better executed as sequential phases with test gates between each

Execution approach: Builder persona, phase-by-phase, test after each phase.

---

## Success Criteria

1. `sourcestack.py sweep --geo nyc --all-archetypes --dry-run` produces valid API payload
2. `sourcestack.py review --pending` shows jobs with freshness scores and geo tags
3. `sourcestack.py publish` successfully creates pages in Notion Job board DB
4. `sourcestack.py prune --dry-run` correctly identifies 30/60/90 day lifecycle transitions
5. Daily credit usage tracked and capped at 500
6. Weekly pruning agent runs without errors
7. V can do full cycle via prompting: "show me new NYC backend jobs" → "approve these" → "publish"

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| SourceStack API key not set | Graceful error message pointing to Settings > Advanced |
| Notion property type migration breaks existing data | Create new properties alongside old, migrate data, then remove old |
| Credit cap too aggressive for broad sweeps | Monitor actual usage in first week, adjust cap if needed |
| Archetype titles too broad → noisy results | Categories double-check filters out non-engineering roles |
| Geo classification misses edge cases (e.g., "remote-first" in NYC) | Conservative: if ambiguous, classify as `unclassified` for manual review |

---

## Learning Landscape

### Build Friction Recommendation
**Recommended:** minimal
**Rationale:** V is familiar with the SourceStack concept and Notion integration pattern. The novel concepts (archetype system, geo routing, lifecycle management) are domain concepts, not deep technical ones. Standard execution with decision points only if architectural surprises emerge.

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| API pagination + credit management | Intermediate | APIs | Medium |
| SQLite schema migrations | Beginner | Databases | ★ High |
| State machines (job lifecycle) | Beginner | Systems Design | ★ High |
| Notion API property types | Beginner | APIs | Medium |

### Decision Points

| ID | Question | Options | Value | Phase |
|----|----------|---------|-------|-------|
| DP-1 | Notion schema migration approach | Create-new-migrate vs in-place | Medium | Phase 3 |

---

## Level Upper Review

*To be completed after V approves plan direction.*
