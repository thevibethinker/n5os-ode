---
created: 2026-02-01
last_edited: 2026-02-01
version: 1.0
provenance: con_TN9WOo9G9cY3zZuh
build_slug: meeting-system-v3
status: planning
---

# PLAN: Meeting Orchestrator v3

**Objective:** Build a Pulse-driven meeting ingestion pipeline that replaces all legacy systems with a single, reliable skill. This is the LAST time we touch this system in Q1 2026.

**Success Criteria:**
1. Single `meeting-ingestion` skill handles full pipeline: Ingest → Identify → Quality Gate → Blocks → Archive
2. All state lives in `manifest.json` (SSOT) with versioned schema
3. Calendar triangulation + CRM enrichment for participant identification
4. HITL queue for uncertainty with SMS notifications
5. Quality harness validates outputs before archival
6. One scheduled agent replaces all legacy MG-* agents
7. Zero orphaned files in Inbox after migration

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Where is microsummary stored? | `manifest.summary` field (not a block) |
| CRM location? | `Personal/Knowledge/Legacy_Inbox/crm/crm.db` (migrate to canonical) |
| HITL format? | JSONL at `N5/review/meetings/hitl-queue.jsonl` |
| Fallback participant ID? | Heuristics + LLM → HITL if uncertain |
| Block gen drop manual? | Yes - V spawns manually to interact |
| MECE split? | Granular (one drop per meeting per task) |

---

## Block Policy: Final Block List

### Design Philosophy
- **Refinement, not compression** - All 27 blocks retained, prompts refined for specificity
- **Smart selector** - LLM picks conditional blocks based on transcript content + V's priorities
- **Zo Take Heed triggers** - B00 scans for verbal cues that activate specific blocks (B07, B14)
- **Prompt quality** - Length follows purpose; some shorter, some longer, all highly specific

---

### External Meetings (17 blocks)

| Code | Name | When | Notes |
|------|------|------|-------|
| **B00** | Zo Take Heed | Always | Scans for deferred intents; triggers B07/B14 |
| **B01** | Detailed Recap | Always | Core summary |
| **B02+B05** | Commitments & Actions | Always | **Merged** - explicit promises + tasks with owners |
| **B03** | Decisions | Always | Key decisions with rationale |
| B04 | Open Questions | Conditional | When unresolved questions exist |
| B06 | Business Context | Conditional | **Company-specific** strategic context |
| B07 | Warm Introductions | Conditional | **Zo Take Heed trigger only** |
| **B08** | Stakeholder Intelligence | Always | Participant insights, communication style |
| B10 | Relationship Trajectory | Conditional | When relationship trajectory discussed |
| B13 | Plan of Action | Conditional | Synthesized next steps across parties |
| B14 | Blurbs Requested | Conditional | **Zo Take Heed trigger only** |
| **B21** | Key Moments | Always | Significant moments, turning points |
| B25 | Deliverable Map | Conditional | When specific deliverables discussed |
| **B26** | Meeting Metadata | Always | Date, participants, duration, purpose |
| B28 | Strategic Intelligence | Conditional | **Broad landscape** implications |
| B32 | Thought Provoking Ideas | Conditional | → Feeds idea system |
| B33 | Decision Rationale | Conditional | → Feeds idea system |

**Always: 7 blocks** | **Conditional: 10 blocks**

---

### Internal Meetings (10 blocks)

| Code | Name | When | Notes |
|------|------|------|-------|
| **B00** | Zo Take Heed | Always | Same as external |
| **B40** | Internal Decisions | Always | Team decisions with context |
| **B41** | Team Coordination | Always | Alignment items, handoffs |
| **B42** | Internal Actions | Always | Internal-only tasks |
| B43 | Resource Allocation | Conditional | When capacity/bandwidth discussed |
| B44 | Process Improvements | Conditional | When workflow changes discussed |
| **B45** | Team Dynamics | Always | **Mandatory** - interpersonal notes |
| B46 | Knowledge Transfer | Conditional | When training/onboarding discussed |
| **B47** | Open Debates | Always | **Mandatory** - unresolved tensions |
| **B48** | Internal Synthesis | Always | Strategic takeaways for leadership |

**Always: 7 blocks** | **Conditional: 3 blocks**

---

### Reflection Blocks - Excluded

R01-R09 and RIX are **not part of meeting processing**. Reserved for future dedicated reflection/transcript ingestion system.

---

### Special Triggers (via B00 Zo Take Heed)

B00 scans transcript for verbal cues and flags specific blocks for generation:

| Trigger Pattern | Activates | Example |
|-----------------|-----------|---------|
| "Zo, draft a blurb..." | B14 Blurbs Requested | "Zo, draft a blurb about David for LinkedIn" |
| "Zo, intro me to..." | B07 Warm Introductions | "Zo, intro me to their CTO" |
| "Zo take heed..." | Captured in B00 | Any deferred intent |
| "Zo, remember..." | Captured in B00 | Things to follow up on |

---

### Internal Team (for meeting type classification)

CRM `is_internal` flag determines meeting type. Current internal team:
- V (Vrijen Attawar) - always internal
- Logan - Careerspan team
- Ilse - Careerspan team  
- Shivam - Careerspan team
- Ankith - Zenny (counts as internal)

All others default to external unless CRM `is_internal = true`.

---

## Architecture Overview

```
Google Drive / Fathom Webhook
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ INBOX (Personal/Meetings/Inbox/)                            │
│                                                             │
│  Raw files → INGEST → Folders with manifest.json            │
│                                                             │
│  manifest.json state machine:                               │
│    raw → ingested → identified → gated → processed → ready  │
│                                                             │
│  Stages:                                                    │
│  1. INGEST: Normalize transcript, extract microsummary      │
│  2. IDENTIFY: Calendar triangulation + CRM lookup           │
│  3. QUALITY_GATE: Validate readiness, trigger HITL if needed│
│  4. BLOCKS: Generate blocks (LLM via /zo/ask)               │
│  5. ARCHIVE: Move to Week-of-*/internal|external/           │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ ARCHIVE (Personal/Meetings/Week-of-YYYY-MM-DD/)             │
│  ├── internal/                                              │
│  │   └── 2026-01-26_Team-Standup/                           │
│  └── external/                                              │
│      └── 2026-01-26_David-x-Careerspan/                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Manifest v3 Schema

```json
{
  "$schema": "manifest-v3",
  "meeting_id": "2026-01-26_David-x-Careerspan",
  "status": "identified",
  "status_history": [
    {"status": "raw", "at": "2026-01-26T10:00:00Z"},
    {"status": "ingested", "at": "2026-01-26T10:01:00Z"},
    {"status": "identified", "at": "2026-01-26T10:02:00Z"}
  ],
  
  "source": {
    "type": "fathom|fireflies|gdrive|manual",
    "original_filename": "...",
    "ingested_at": "..."
  },
  
  "meeting": {
    "date": "2026-01-26",
    "time_utc": "15:00:00",
    "duration_minutes": 45,
    "title": "Careerspan Partnership Discussion",
    "type": "external|internal",
    "summary": "One paragraph microsummary generated during ingest"
  },
  
  "participants": {
    "identified": [
      {"name": "V", "email": "...", "crm_id": 1, "role": "host"},
      {"name": "David", "email": "...", "crm_id": 42, "role": "attendee"}
    ],
    "unidentified": [],
    "confidence": 0.95
  },
  
  "calendar_match": {
    "event_id": "...",
    "confidence": 0.9,
    "method": "timestamp+title"
  },
  
  "quality_gate": {
    "passed": true,
    "checks": {
      "has_transcript": true,
      "participants_identified": true,
      "meeting_type_determined": true,
      "no_hitl_pending": true
    },
    "score": 1.0
  },
  
  "blocks": {
    "policy": "external_standard",
    "requested": ["B00", "B01", "B03", "B05", "B08", "B26"],
    "generated": ["B00", "B01"],
    "failed": [],
    "skipped": []
  },
  
  "hitl": {
    "queue_id": null,
    "reason": null,
    "resolved_at": null
  },
  
  "timestamps": {
    "created_at": "...",
    "ingested_at": "...",
    "identified_at": "...",
    "gated_at": "...",
    "processed_at": "...",
    "archived_at": null
  }
}
```

---

## Drop Architecture (Pulse Build)

### STREAM 0: Block Compression (Auto-spawn, sequential)

| Drop | Name | Description | Dependencies |
|------|------|-------------|--------------|
| D0.1 | Block Inventory Analysis | Analyze all existing B* prompts, identify overlaps, propose merges | None |
| D0.2 | Super Block Prompts | Write compressed prompts for S00-S08 and SI00-SI04 (250 words max each) | D0.1 |
| D0.3 | Block Index Creation | Create BLOCK_INDEX.yaml with recipes | D0.2 |
| D0.4 | Smart Selector | Build LLM-powered selector that reads transcript + priorities | D0.3 |

**Gate:** V reviews super block prompts before Stream 1

---

### STREAM 1: Audit & Migration (Auto-spawn)

| Drop | Name | Description | Dependencies |
|------|------|-------------|--------------|
| D1.1 | Inventory Audit | Scan Inbox + root meetings, catalog all shapes, generate migration plan | None |
| D1.2 | Audit Verification | Verify D1.1 output, spot-check paths, confirm no collisions | D1.1 |
| D1.3 | CRM Migration | Move CRM from Legacy_Inbox to canonical location, validate schema | D1.1 |
| D1.4 | Legacy Converter | Build converter for legacy manifest → v3 manifest | D1.2 |

**Gate:** V reviews audit report before Stream 2

---

### STREAM 2: Spec & Schema (Auto-spawn, sequential)

| Drop | Name | Description | Dependencies |
|------|------|-------------|--------------|
| D2.1 | Manifest Schema | Define manifest-v3.schema.json with JSON Schema validation | D1.4 |
| D2.2 | Meeting ID Convention | Document naming rules + transformation examples | D2.1 |
| D2.3 | Block Picker Policy | Define rules, confidence thresholds, token budgets | D2.1 |
| D2.4 | Quality Harness Spec | Define checks, scoring, retry logic | D2.1 |
| D2.5 | HITL Queue Spec | Define schema, reporting location, SMS trigger rules | D2.1 |

**Gate:** V reviews specs before Stream 3

---

### STREAM 3: Core Processing Modules (Auto-spawn, parallel after D2.5)

| Drop | Name | Description | Dependencies |
|------|------|-------------|--------------|
| D3.1 | Ingest Module | Convert formats → transcript.md + microsummary, create manifest | D2.1 |
| D3.2 | Calendar Triangulation | Query Google Calendar, match by timestamp + title, score confidence | D2.1 |
| D3.3 | CRM Enricher | Query local CRM, classify internal/external, surface unknowns | D1.3, D2.5 |
| D3.4 | Quality Gate | Validate readiness, trigger HITL if needed, compute score | D2.4, D2.5 |
| D3.5 | CLI Update | Update meeting_cli.py with new state machine + modules | D3.1-D3.4 |

**Gate:** V reviews modules before Stream 4

---

### STREAM 4: Block Generation (MANUAL spawn - V interacts)

| Drop | Name | Description | Dependencies |
|------|------|-------------|--------------|
| D4.1 | Block Picker v2 | Apply policy, select blocks, explain why | D2.3 |
| D4.2 | Block Generator | Spawn /zo/ask per block, collect results, handle failures | D4.1 |
| D4.3 | Quality Check | Validate block outputs, score, recommend retries | D2.4, D4.2 |

**Gate:** V reviews block generation before Stream 5

---

### STREAM 5: Archive & Cleanup (Auto-spawn)

| Drop | Name | Description | Dependencies |
|------|------|-------------|--------------|
| D5.1 | Archive Module | Move complete meetings to Week-of-*/internal|external/ | D4.3 |
| D5.2 | Migration Execute | Run legacy converter on all backlog meetings | D1.4, D5.1 |
| D5.3 | Cleanup | Remove orphans, verify structure, generate report | D5.2 |

---

### STREAM 6: Integration & Scheduling (Auto-spawn)

| Drop | Name | Description | Dependencies |
|------|------|-------------|--------------|
| D6.1 | Integration Test | Run 5-10 meetings through full pipeline, validate | D5.1 |
| D6.2 | Scheduled Agent | Create new agent, disable old MG-* agents | D6.1 |
| D6.3 | Documentation | Update SKILL.md, create runbook | D6.2 |

---

## Affected Files

### New Files
- `Skills/meeting-ingestion/references/manifest-v3.schema.json`
- `Skills/meeting-ingestion/references/meeting-id-convention.md`
- `Skills/meeting-ingestion/references/block-picker-v2-policy.md`
- `Skills/meeting-ingestion/references/quality-harness-checks.md`
- `Skills/meeting-ingestion/references/hitl-queue-spec.md`
- `Skills/meeting-ingestion/scripts/ingest.py` (new or rewrite)
- `Skills/meeting-ingestion/scripts/identify.py` (calendar + CRM)
- `Skills/meeting-ingestion/scripts/quality_gate.py`
- `Skills/meeting-ingestion/scripts/block_picker.py`
- `Skills/meeting-ingestion/scripts/block_generator.py`
- `N5/review/meetings/hitl-queue.jsonl`

### Modified Files
- `Skills/meeting-ingestion/SKILL.md`
- `Skills/meeting-ingestion/scripts/meeting_cli.py`
- `Skills/meeting-ingestion/scripts/stage.py` → absorbed into ingest.py
- `Skills/meeting-ingestion/scripts/process.py` → split into modules
- `Skills/meeting-ingestion/scripts/archive.py`
- `N5/config/meeting_config.py` (add new constants)
- `N5/scripts/meeting_registry.py` (if used)

### CRM Migration
- FROM: `Personal/Knowledge/Legacy_Inbox/crm/crm.db`
- TO: `N5/data/crm.db` (canonical location)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Legacy data loss during migration | Dry-run first, snapshot before execute |
| Calendar API rate limits | Batch queries, cache results |
| CRM schema mismatch | Validate schema before migration |
| Block generation cost (tokens) | Quality gate prevents bad inputs |
| HITL queue floods | Rate limit SMS, batch notifications |

---

## Checklist

### Stream 1: Audit & Migration
- [ ] D1.1: Inventory audit complete
- [ ] D1.2: Audit verified
- [ ] D1.3: CRM migrated
- [ ] D1.4: Legacy converter built
- [ ] V approval gate

### Stream 2: Spec & Schema
- [ ] D2.1: Manifest schema defined
- [ ] D2.2: Meeting ID convention documented
- [ ] D2.3: Block picker policy defined
- [ ] D2.4: Quality harness spec complete
- [ ] D2.5: HITL queue spec complete
- [ ] V approval gate

### Stream 3: Core Processing
- [ ] D3.1: Ingest module built
- [ ] D3.2: Calendar triangulation built
- [ ] D3.3: CRM enricher built
- [ ] D3.4: Quality gate built
- [ ] D3.5: CLI updated
- [ ] V approval gate

### Stream 4: Block Generation (MANUAL)
- [ ] D4.1: Block picker v2 built
- [ ] D4.2: Block generator built
- [ ] D4.3: Quality check built
- [ ] V approval gate

### Stream 5: Archive & Cleanup
- [ ] D5.1: Archive module built
- [ ] D5.2: Migration executed
- [ ] D5.3: Cleanup complete

### Stream 6: Integration & Scheduling
- [ ] D6.1: Integration test passed
- [ ] D6.2: Scheduled agent created
- [ ] D6.3: Documentation complete

---

## Notes for V

1. **STREAM 4 is MANUAL** - I'll create the drop briefs but you spawn them when ready
2. **Gates between streams** - I'll post a summary after each stream, you approve before next
3. **LLM for semantic work** - All participant identification, block generation, microsummary use /zo/ask
4. **Python for mechanical** - File operations, state management, CLI, database queries
5. **HITL queue** - Every item gets an ID, you can respond "HITL-001 is Logan" and I'll parse it
