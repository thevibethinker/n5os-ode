---
name: meeting-ingestion
description: Meeting ingestion pipeline v3 with calendar triangulation, CRM enrichment, quality gates, HITL queue, and intelligent block selection. Unified CLI for transcript processing from ingest to archive.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer  
  version: "3.0.0"
  created: 2026-01-26
  rebuilt: 2026-02-09
  build_id: meeting-system-v3
---

# Meeting Ingestion Skill v3

Complete meeting transcript processing pipeline: download from Google Drive → ingest → identify participants → quality gate → intelligent block generation → archive to weekly folders.

## Quick Start

```bash
# Full pipeline for new transcript
python3 Skills/meeting-ingestion/scripts/meeting_cli.py ingest /path/to/transcript.md
python3 Skills/meeting-ingestion/scripts/meeting_cli.py identify <meeting-folder>
python3 Skills/meeting-ingestion/scripts/meeting_cli.py gate <meeting-folder> 
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process <meeting-folder>
python3 Skills/meeting-ingestion/scripts/meeting_cli.py archive --execute

# Or use orchestrator (processes entire pipeline)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py tick
```

## v3 Pipeline Overview

```
┌─────────────────────┐
│ Google Drive        │
│   ├─ transcript.md  │
│   └─ meeting.jsonl  │
└─────────┬───────────┘
          │ pull
          ▼
┌─────────────────────┐
│ RAW FILES           │
│ (Inbox root)        │
└─────────┬───────────┘
          │ ingest
          ▼
┌─────────────────────────────────────────┐
│ INGESTED                                │
│  2026-01-26_David-x-Careerspan/         │
│    ├─ transcript.md                     │
│    └─ manifest.json {status: ingested}  │
└─────────┬───────────────────────────────┘
          │ identify
          ▼
┌─────────────────────────────────────────┐
│ IDENTIFIED                              │  
│  2026-01-26_David-x-Careerspan/         │
│    ├─ transcript.md                     │
│    └─ manifest.json {status: identified}│
│        ├─ participants: [...] ✓         │
│        ├─ meeting_type: external ✓      │
│        └─ calendar_match: {...} ✓       │
└─────────┬───────────────────────────────┘
          │ gate
          ▼
┌─────────────────────────────────────────┐
│ GATED                                   │
│  2026-01-26_David-x-Careerspan/         │
│    ├─ transcript.md                     │
│    └─ manifest.json {status: gated}     │
│        └─ quality_gate: {passed: true} ✓│
└─────────┬───────────────────────────────┘
          │ process
          ▼
┌─────────────────────────────────────────┐
│ PROCESSED                               │
│  2026-01-26_David-x-Careerspan/         │
│    ├─ transcript.md                     │
│    ├─ B00_ZO_TAKE_HEED.md               │
│    ├─ B01_DETAILED_RECAP.md             │
│    ├─ B02_B05_COMMITMENTS_ACTIONS.md    │
│    ├─ B03_DECISIONS.md                  │  
│    ├─ B08_STAKEHOLDER_INTELLIGENCE.md   │
│    ├─ B21_KEY_MOMENTS.md                │
│    ├─ B26_MEETING_METADATA.md           │
│    └─ manifest.json {status: processed} │
└─────────┬───────────────────────────────┘
          │ archive
          ▼
┌─────────────────────────────────────────┐
│ ARCHIVED                                │
│  Week-of-2026-01-20/external/           │
│    └─ 2026-01-26_David-x-Careerspan/    │
└─────────────────────────────────────────┘
```

## Commands Reference

### v3 Pipeline Commands (Recommended)

#### `ingest` - Raw → Ingested
Convert raw transcripts into meeting folders with v3 manifest.

```bash
python3 meeting_cli.py ingest <path> [--dry-run] [--json]

# Examples
python3 meeting_cli.py ingest transcript.md          # Single file 
python3 meeting_cli.py ingest meeting-folder/       # Folder with transcript
python3 meeting_cli.py ingest . --dry-run          # Preview all in current dir
```

**What it does:**
- Detects format (JSONL vs markdown vs folder)
- Extracts participants, date, duration from content
- Creates meeting folder with standard naming: `YYYY-MM-DD_Participant-Name`
- Generates v3 manifest.json with status: "ingested"
- Moves transcript to standardized `transcript.md`

#### `identify` - Calendar + CRM Enrichment
Match meeting to calendar and enrich participant data from CRM.

```bash
python3 meeting_cli.py identify <meeting-folder> [--dry-run] [--json]

# Example
python3 meeting_cli.py identify 2026-01-26_David-x-Careerspan/
```

**What it does:**
- **Calendar triangulation**: Queries Google Calendar by date/time/title, scores matches
- **CRM enrichment**: Looks up participants in local CRM database
- **Type classification**: Determines internal vs external meeting type
- **Confidence scoring**: Tracks identification confidence levels
- **HITL escalation**: Queues for manual review if confidence too low
- Updates manifest status: "ingested" → "identified"

#### `gate` - Quality Validation
Validate meeting readiness using 16 quality checks.

```bash
python3 meeting_cli.py gate <meeting-folder> [--dry-run] [--verbose] [--json]

# Example  
python3 meeting_cli.py gate 2026-01-26_David-x-Careerspan/ --verbose
```

**Quality checks include:**
- **Transcript validation**: Length, format, encoding, duration consistency
- **Participant confidence**: ≥0.7 overall, host identified, external participants verified
- **Calendar matching**: ≥0.6 confidence or manual override
- **Type consistency**: Meeting type aligns with participant roster

**Pass/Fail logic:**
- **PASS**: Overall score ≥0.8, no critical failures
- **FAIL + HITL**: Participant ID <0.5, encoding corruption, critical failures  
- **FAIL + RETRY**: Transcript too short, temporary API failures

Updates manifest status: "identified" → "gated"

#### `process` - Block Generation
Generate intelligence blocks using smart selector + LLM block generation.

```bash
python3 meeting_cli.py process <meeting-folder> [--blocks B01,B05] [--dry-run]

# Examples
python3 meeting_cli.py process 2026-01-26_David-x-Careerspan/    # Smart selection
python3 meeting_cli.py process 2026-01-26_David-x-Careerspan/ --blocks B01,B08  # Manual
```

**Smart Block Selection:**
1. **Recipe selection**: Chooses from 6 base recipes based on meeting type + participants
2. **LLM analysis**: `/zo/ask` analyzes transcript for conditional block triggers
3. **Priority weighting**: Considers V's current focus areas (business, career, personal, health, relationship)
4. **Zo Take Heed scanning**: Detects verbal cues like "intro me to", "draft a blurb"

**Block categories:**
- **Always blocks**: Generated for every meeting of this type (7-9 blocks)
- **Conditional blocks**: Generated when content triggers detected (3-10 blocks)
- **Triggered blocks**: Generated via B00 Zo Take Heed patterns (B07, B14)

Updates manifest status: "gated" → "processed"

#### `tick` - Orchestrated Pipeline
Process entire pipeline automatically (used by scheduled agent).

```bash
python3 meeting_cli.py tick [--dry-run] [--batch-size N]

# Used by Meeting Orchestrator v3 agent (runs daily at 6 AM ET)
```

**Pipeline sequence:**
1. Pull new transcripts from Google Drive
2. Stage raw files for processing  
3. Run identification pipeline on staged meetings
4. Apply quality gates with HITL escalation
5. Process gated meetings with intelligent block selection
6. Archive completed meetings to weekly folders

### Legacy Commands (v2 Compatibility)

#### `status` - Queue Status
Show current pipeline state across all stages.

```bash
python3 meeting_cli.py status

# Output example:
# Raw files (needs ingest): 2
# Ingested (needs identify): 1  
# Identified (needs gate): 3
# Gated (needs process): 1
# Processed (needs archive): 4
# Total archived: 847
```

#### `archive` - Move to Weekly Folders
Move completed meetings to `Week-of-YYYY-MM-DD/internal|external/` structure.

```bash
python3 meeting_cli.py archive [--execute] [--batch-size N]

# Preview (default)
python3 meeting_cli.py archive

# Execute  
python3 meeting_cli.py archive --execute
```

#### `stage` - Legacy v2 Staging
Convert v2-style raw files to folder structure (compatibility mode).

```bash
python3 meeting_cli.py stage [--dry-run]
```

#### `fix` - Repair Malformed State
Quarantine orphaned files and repair Inbox state.

```bash
python3 meeting_cli.py fix [--dry-run]
```

## Intelligence Blocks

Meeting Ingestion v3 uses a **smart block selector** that intelligently chooses which blocks to generate based on transcript content, meeting type, participants, and V's current priorities.

### Block Recipes

| Recipe | Use Case | Always | Conditional | Total |
|--------|----------|--------|-------------|-------|
| `external_standard` | Default external meetings | 7 | 10 | 17 |
| `external_sales` | Sales/partnership meetings | 8 | 8 | 16 |
| `external_investor` | Investor meetings | 9 | 6 | 15 |
| `internal_standup` | Team standups | 5 | 4 | 9 |
| `internal_strategy` | Strategy sessions | 7 | 3 | 10 |
| `internal_retrospective` | Retrospectives | 6 | 4 | 10 |

### External Meeting Blocks

**Always Generated (7 blocks):**
- **B00** - Zo Take Heed (scans for deferred intents, triggers B07/B14)
- **B01** - Detailed Recap (core meeting summary)
- **B02_B05** - Commitments & Actions (merged: promises + tasks with owners)
- **B03** - Decisions (key decisions with rationale)
- **B08** - Stakeholder Intelligence (participant insights)
- **B21** - Key Moments (significant moments, turning points)
- **B26** - Meeting Metadata (date, participants, duration, purpose)

**Conditionally Generated (10 blocks):**
- **B04** - Open Questions (when unresolved questions exist)
- **B06** - Business Context (company-specific strategic context)
- **B07** - Warm Introductions (Zo Take Heed trigger only)
- **B10** - Relationship Trajectory (when trajectory discussed)
- **B13** - Plan of Action (synthesized next steps)
- **B14** - Blurbs Requested (Zo Take Heed trigger only)
- **B25** - Deliverable Map (when deliverables discussed)
- **B28** - Strategic Intelligence (broad landscape implications)
- **B32** - Thought Provoking Ideas (feeds idea system)
- **B33** - Decision Rationale (feeds idea system)

### Internal Meeting Blocks

**Always Generated (7 blocks):**
- **B00** - Zo Take Heed
- **B40** - Internal Decisions (team decisions with context)
- **B41** - Team Coordination (alignment, handoffs)
- **B42** - Internal Actions (internal tasks)
- **B45** - Team Dynamics (interpersonal notes)
- **B47** - Open Debates (unresolved tensions)
- **B48** - Internal Synthesis (strategic takeaways)

**Conditionally Generated (3 blocks):**
- **B43** - Resource Allocation (capacity/bandwidth discussions)
- **B44** - Process Improvements (workflow changes)
- **B46** - Knowledge Transfer (training/onboarding)

### Special Triggers (Zo Take Heed)

**B07 (Warm Introductions)** triggered by:
- "intro me to", "introduce me to", "connect me with", "make an introduction"

**B14 (Blurbs Requested)** triggered by:  
- "draft a blurb", "write a blurb", "blurb about", "create a blurb"

**B00 (Deferred Intents)** triggered by:
- "zo take heed", "zo, remember", "zo, follow up on", "zo, note that"

## HITL Queue System

When automated processing cannot complete reliably, items are escalated to the **Human-In-The-Loop (HITL) queue** for V's review.

### Queue Location
`N5/review/meetings/hitl-queue.jsonl`

### Escalation Triggers
- **Participant identification confidence <0.5** (unknown speakers)
- **Calendar match confidence <0.6** (no clear calendar match)
- **Meeting topic unclear** (ambiguous purpose)
- **Encoding corruption** (transcript quality issues)
- **Duplicate detection uncertainty** (potential duplicate meeting)

### Priority Levels
- **P0 (Immediate)**: System errors, encoding corruption, critical stakeholder failures
- **P1 (Standard)**: Low participant confidence, calendar match failures
- **P2 (Batch)**: Minor validation issues, borderline scores

### SMS Notifications
V receives SMS notifications for:
- P0 items (immediately)
- P1 items (hourly digest) 
- Weekly digest of all HITL activity

## Quality Gate Specification

The quality gate performs **16 distinct checks** across 4 pipeline stages:

### Pre-processing Stage (4 checks)
- **transcript_length**: ≥300 characters actual content
- **transcript_format**: Valid UTF-8, speaker indicators
- **meeting_duration_consistency**: Word count within 50% of expected
- **transcript_encoding**: UTF-8 compliant, no artifacts

### Identification Stage (5 checks)  
- **participant_confidence**: Overall confidence ≥0.7
- **host_identified**: At least one participant has role "host"
- **external_participant_verification**: External meetings have ≥1 non-V participant
- **calendar_match_score**: Match confidence ≥0.6 or manual override
- **meeting_type_consistency**: Type aligns with participant roster

### Block Generation Stage (4 checks)
- **block_count_reasonable**: Generated blocks within expected range
- **block_quality_score**: LLM quality assessment ≥0.7
- **missing_critical_blocks**: All always-blocks generated successfully
- **block_file_integrity**: All block files valid markdown with frontmatter

### Post-processing Stage (3 checks)
- **archive_readiness**: All required metadata present
- **duplicate_detection**: No conflicts with existing meetings
- **pipeline_completion**: All pipeline stages completed successfully

### Pass/Fail Logic
- **PASS**: Overall score ≥0.8, no critical failures, no HITL escalations
- **FAIL + HITL**: Critical failures requiring human intervention
- **FAIL + RETRY**: Temporary issues (API failures, short transcripts)
- **PASS with WARNING**: Optional checks failed but core requirements met

## Manifest v3 Schema

Every meeting folder contains a `manifest.json` following the v3 schema:

```json
{
  "manifest_version": "3.0",
  "meeting_id": "2026-01-26_David-x-Careerspan",
  "date": "2026-01-26",
  "participants": [
    {"name": "David", "role": "external", "confidence": 0.95},
    {"name": "V", "role": "host", "confidence": 1.0}
  ],
  "meeting_type": "external",
  "status": "processed",
  
  "source": {
    "format": "markdown", 
    "original_path": "/path/to/transcript.md",
    "ingested_at": "2026-01-26T10:30:00Z"
  },
  
  "calendar_match": {
    "matched": true,
    "confidence": 0.85,
    "event_id": "abc123",
    "event_title": "David x Careerspan Partnership"
  },
  
  "crm_data": {
    "david": {
      "company": "InvestCorp",
      "title": "Partner", 
      "last_interaction": "2025-12-15",
      "relationship": "business"
    }
  },
  
  "quality_gate": {
    "passed": true,
    "score": 0.92,
    "checks": {
      "has_transcript": true,
      "participants_identified": true,
      "meeting_type_determined": true, 
      "no_hitl_pending": true
    },
    "executed_at": "2026-01-26T10:45:00Z"
  },
  
  "blocks": {
    "recipe": "external_standard",
    "requested": ["B00", "B01", "B02_B05", "B03", "B08", "B21", "B26"],
    "generated": ["B00", "B01", "B02_B05", "B03", "B08", "B21", "B26"],
    "failed": [],
    "conditional_selected": ["B06", "B28"],
    "conditional_skipped": ["B04", "B07", "B10", "B13", "B14", "B25", "B32", "B33"],
    "triggered": []
  },
  
  "hitl": {
    "queue_id": null,
    "reason": null, 
    "resolved_at": null
  },
  
  "timestamps": {
    "created_at": "2026-01-26T10:30:00Z",
    "ingested_at": "2026-01-26T10:30:00Z", 
    "identified_at": "2026-01-26T10:35:00Z",
    "gated_at": "2026-01-26T10:45:00Z",
    "processed_at": "2026-01-26T11:15:00Z",
    "archived_at": null
  }
}
```

## State Machine

Meeting processing follows a strict state progression:

| Status | Description | Next Action |
|--------|-------------|-------------|
| `raw` | Unprocessed file in Inbox root | → ingest |  
| `ingested` | Folder created, transcript standardized | → identify |
| `identified` | Participants + calendar + CRM data added | → gate |
| `gated` | Quality validation passed | → process |
| `processed` | Intelligence blocks generated | → archive |
| `archived` | Moved to Week-of folder | ✓ Complete |
| `hitl_pending` | Escalated to HITL queue | → human review |
| `failed` | Unrecoverable error | → manual intervention |

State transitions are tracked in manifest.json with timestamps for audit purposes.

## Directory Structure

```
Skills/meeting-ingestion/
├── SKILL.md                    # This file
├── scripts/                    # CLI and processing modules
│   ├── meeting_cli.py          # Unified CLI v3
│   ├── ingest.py              # Raw → ingested conversion
│   ├── calendar_match.py       # Google Calendar triangulation
│   ├── crm_enricher.py        # CRM participant enrichment  
│   ├── quality_gate.py        # Quality validation (16 checks)
│   ├── block_selector.py      # Smart block selection
│   ├── block_generator.py     # LLM block generation
│   ├── hitl.py                # HITL queue management
│   ├── archive.py             # Weekly folder archival
│   ├── pull.py                # Google Drive download
│   ├── stage.py               # Legacy v2 compatibility
│   ├── processor.py           # Legacy processor
│   ├── validate_manifest.py   # Manifest schema validation
│   └── manifest_converter.py  # v2 → v3 migration
├── references/                 # Documentation and specs  
│   ├── manifest-v3.schema.json     # JSON Schema for manifest
│   ├── meeting-id-convention.md    # Naming standards
│   ├── block-picker-v2-policy.md   # Smart selection rules
│   ├── quality-harness-checks.md   # Quality gate specification
│   ├── hitl-queue-spec.md          # HITL queue schema
│   ├── quality-gate-docs.md        # Quality validation docs
│   ├── block-quality-thresholds.md # Block quality scoring
│   └── legacy_prompts.md           # Migration notes
└── assets/                     # (none currently)
```

## Configuration

### Drive Locations
Drive folder IDs in `N5/config/drive_locations.yaml`:
```yaml
meetings:
  transcripts_inbox: "YOUR_FOLDER_ID"
```

### Meeting Registry
Meeting statistics and deduplication tracking:
- **Location**: `N5/data/meeting_registry.db` (SQLite)
- **Purpose**: Track all processed meetings, detect duplicates, maintain statistics
- **Schema**: meeting_id, date, participants, type, blocks_generated, archived_location

### CRM Database
Participant information storage:
- **Location**: `Personal/Knowledge/CRM/crm.db` (migrated from Legacy_Inbox)
- **Purpose**: Participant lookup, relationship classification, contact enrichment
- **Integration**: Automatic lookup during identification stage

## Typical Workflows

### Daily Automated Processing
The **Meeting Orchestrator v3** scheduled agent runs daily at 6 AM ET:

```bash
# Agent instruction (simplified):
python3 Skills/meeting-ingestion/scripts/meeting_cli.py tick --batch-size 10
```

This processes the complete pipeline:
1. Pull from Google Drive (up to 10 new transcripts)
2. Ingest raw files into meeting folders  
3. Identify participants via calendar + CRM
4. Validate quality and escalate to HITL if needed
5. Generate intelligence blocks using smart selector
6. Archive completed meetings to weekly folders

### Manual Single Meeting Processing

```bash
# Process a specific raw transcript
cd /home/workspace
python3 Skills/meeting-ingestion/scripts/meeting_cli.py ingest transcript.md

# Continue pipeline manually  
MEETING=$(ls -1 Personal/Meetings/Inbox/2026-*/ | tail -1)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py identify "$MEETING"
python3 Skills/meeting-ingestion/scripts/meeting_cli.py gate "$MEETING" --verbose
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process "$MEETING" 
python3 Skills/meeting-ingestion/scripts/meeting_cli.py archive --execute
```

### HITL Queue Management

```bash
# Check queue status
python3 Skills/meeting-ingestion/scripts/hitl.py status

# Resolve HITL item (after manual review)
python3 Skills/meeting-ingestion/scripts/hitl.py resolve HITL-20260126-001 --resolution "participant_identified" --data '{"participant": "David Chen", "company": "InvestCorp"}'

# Clear resolved items  
python3 Skills/meeting-ingestion/scripts/hitl.py cleanup --older-than 7d
```

## Troubleshooting

### Common Issues

**"No transcript found in meeting folder"**
- Ensure transcript file exists as `transcript.md` in meeting folder
- Run `ingest` first if you have a raw file
- Check file permissions and encoding

**"Participant identification failed"** 
- Check if speakers are clearly labeled in transcript (e.g., "John:", "V:")
- Review CRM database for participant entries
- Low confidence triggers HITL escalation (expected behavior)

**"Quality gate failed"**
- Run with `--verbose` to see which specific checks failed
- Common failures: transcript too short (<300 chars), encoding issues, missing participants
- Check HITL queue for escalated items: `hitl.py status`

**"Block generation failed"**
- Verify `ZO_CLIENT_IDENTITY_TOKEN` environment variable is set  
- Check if meeting passed quality gate first
- Review block selector output: `block_selector.py <meeting> --json`

**"Calendar match confidence too low"**
- Verify Google Calendar integration is working
- Check if meeting date/time are extracted correctly from transcript
- Low confidence triggers HITL escalation for manual calendar linking

**"Meeting stuck in processing state"**
- Check manifest.json for error details
- Re-run specific pipeline stage: `meeting_cli.py process <meeting>`
- Check logs for block generation failures

### Pipeline State Recovery

**Reset meeting to earlier stage:**
```bash
# Reset to identification stage (if processing failed)
python3 Skills/meeting-ingestion/scripts/validate_manifest.py <meeting> --reset-to identified

# Reset to ingested stage (if identification failed)  
python3 Skills/meeting-ingestion/scripts/validate_manifest.py <meeting> --reset-to ingested
```

**Repair orphaned files:**
```bash
# Quarantine orphaned blocks and repair structure
python3 meeting_cli.py fix --dry-run      # Preview
python3 meeting_cli.py fix                # Execute
```

**Validate manifest integrity:**
```bash
# Check manifest against v3 schema
python3 Skills/meeting-ingestion/scripts/validate_manifest.py <meeting>/manifest.json

# Batch validate all meetings in Inbox
python3 Skills/meeting-ingestion/scripts/validate_manifest.py Personal/Meetings/Inbox/ --recursive
```

### Error Codes

| Code | Meaning | Action |
|------|---------|---------|
| `INGEST_001` | Invalid transcript format | Check file encoding and content |
| `IDENTIFY_002` | Calendar API failure | Retry later or manually link |
| `GATE_003` | Quality threshold not met | Review checks, possibly escalate to HITL |
| `PROCESS_004` | Block generation API failure | Check ZO_CLIENT_IDENTITY_TOKEN |
| `ARCHIVE_005` | Naming collision detected | Resolve manually or use collision suffix |
| `HITL_006` | HITL queue item requires attention | Review HITL queue and resolve |

## Migration from v2

The v3 system is fully backward compatible with v2 meeting folders. Legacy folders are automatically detected and converted:

### Key Changes from v2

**State Management:**
- v2: Folder name suffixes (`_[P]`, `_[B]`, etc.)  
- v3: manifest.json status field

**Block Selection:**
- v2: Fixed block lists based on meeting type
- v3: Smart LLM-powered selector with conditional blocks

**Participant Identification:** 
- v2: Manual or heuristic-based
- v3: Calendar triangulation + CRM enrichment with confidence scoring

**Quality Assurance:**
- v2: Basic validation
- v3: 16-check quality gate with HITL escalation

**Pipeline Stages:**
- v2: pull → stage → process → archive  
- v3: ingest → identify → gate → process → archive

### Migration Process

Existing v2 folders are automatically converted when processed:

1. **Detection**: System detects v2 folder structure (missing manifest.json)
2. **Conversion**: `manifest_converter.py` creates v3 manifest from folder state
3. **Backfill**: Missing data (calendar, CRM) is populated where possible
4. **Validation**: Converted manifest passes through quality gate
5. **Processing**: Continues with v3 pipeline

No manual intervention required - migration happens seamlessly during normal processing.

## Performance and Limits

### Batch Sizes
- **Default batch size**: 5 meetings per operation
- **Maximum recommended**: 10 meetings (prevent API rate limits)
- **HITL queue**: No batch limit (items processed individually)

### API Rate Limits
- **Google Calendar**: 1000 requests/day (100 meetings)
- **Zo Ask API**: 50 requests/hour per meeting (10-15 blocks avg)
- **Automatic retries**: 3 attempts with exponential backoff

### Storage Estimates
- **Average meeting**: 2-5 MB (transcript + 7-12 blocks)
- **Annual storage**: ~1-2 GB (500 meetings/year)
- **Archive compression**: Weekly folders reduce directory traversal

### Quality Gate Performance
- **Processing time**: 2-3 seconds per meeting
- **Pass rate**: ~85% (15% escalate to HITL)
- **Common failures**: Short transcripts (8%), low participant confidence (5%), calendar mismatch (2%)

---

## System Dependencies

- **Python 3.8+** with pathlib, json, sqlite3
- **Google Calendar API** access (for calendar triangulation)
- **Zo Ask API** access (ZO_CLIENT_IDENTITY_TOKEN required)
- **Local CRM database** (SQLite, automatically created if missing)
- **Meeting registry** (SQLite, automatically maintained)

## Related Systems

- **Meeting Orchestrator v3**: Scheduled agent (daily 6 AM ET) that runs `tick` command
- **HITL Review System**: Manual review queue at `N5/review/meetings/hitl-queue.jsonl`
- **Block Prompt Library**: Centralized prompts at `Prompts/Blocks/`
- **Content Library**: Processed blocks can be ingested for knowledge management
- **Meeting Registry**: Statistics and deduplication database

---

*Meeting Ingestion Skill v3.0.0 | Built February 2026 | Build ID: meeting-system-v3*