---
name: meeting-ingestion
description: Meeting ingestion pipeline v3 with calendar triangulation, CRM enrichment, org classification, quality gates, HITL queue, and canonical S-shape generation. Unified CLI for transcript processing from ingest to archive.
compatibility: Created for Zo Computer
metadata:
  author: <YOUR_HANDLE>.zo.computer  
  version: "3.2.0"
  created: 2026-01-26
  rebuilt: 2026-03-17
  last_modified: 2026-04-20
  build_id: meeting-system-v3
---

# Meeting Ingestion Skill v3

Complete meeting transcript processing pipeline with multi-source intake: Google Drive, Fathom, Fireflies, Pocket, and manual transcript import. Unified CLI for transcript processing from ingest to archive, plus intake health checks and historical backfill.

## Canonical Processing Model

The current canonical generation surface is **S-shape based**.

- `file 'Skills/meeting-ingestion/scripts/run_shapes.py'` is the primary shape generator
- `file 'N5/lib/meeting_shapes.py'` defines shape selection, filenames, prompts, and post-processors
- `file 'Skills/meeting-ingestion/scripts/process.py'` as the orchestration bridge that routes gated meetings into canonical shape generation by default

Legacy B-block scripts remain in the repo only for backward compatibility, manual override flows, and migration support. They are not the canonical generation model.

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

# Intake management
python3 Skills/meeting-ingestion/scripts/meeting_cli.py check
python3 Skills/meeting-ingestion/scripts/meeting_cli.py backfill --source all --from 2026-02-01 --to 2026-03-10 --dry-run
python3 Skills/meeting-ingestion/scripts/meeting_cli.py drive-import --scan
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
│  YYYY-MM-DD_Participant/                │
│    ├─ transcript.md                     │
│    └─ manifest.json {status: ingested}  │
└─────────┬───────────────────────────────┘
          │ identify
          ▼
┌─────────────────────────────────────────┐
│ IDENTIFIED                              │
│  YYYY-MM-DD_Participant/                │
│    ├─ transcript.md                     │
│    └─ manifest.json {status: identified}│
│        ├─ participants: [...]           │
│        ├─ meeting_type: external        │
│        └─ calendar_match: {...}         │
└─────────┬───────────────────────────────┘
          │ gate
          ▼
┌─────────────────────────────────────────┐
│ GATED                                   │
│  YYYY-MM-DD_Participant/                │
│    ├─ transcript.md                     │
│    └─ manifest.json {status: gated}     │
│        └─ quality_gate: {passed: true}  │
└─────────┬───────────────────────────────┘
          │ process
          ▼
┌─────────────────────────────────────────┐
│ PROCESSED                               │
│  YYYY-MM-DD_Participant/                │
│    ├─ transcript.md                     │
│    ├─ S01_CONTEXT.md                    │
│    ├─ S02_ACTIONS.md                    │
│    ├─ S03_EVIDENCE.md                   │
│    ├─ S04_PEOPLE.md                     │
│    ├─ S05_WISDOM.md                     │
│    ├─ S06_RECAP.md                      │
│    ├─ S07_ZO_DIRECTIVES.md              │
│    ├─ S08_ZO_INTEL.md                   │
│    ├─ PP_GRAPH_EDGES.jsonl              │
│    └─ manifest.json {status: processed} │
└─────────┬───────────────────────────────┘
          │ closeout + archive
          ▼
┌─────────────────────────────────────────┐
│ ARCHIVED                                │
│  Week-of-YYYY-MM-DD/external/           │
│    └─ YYYY-MM-DD_Participant/           │
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
- **Metadata quality assessment**: Detects bare transcripts (no speakers, no participant context) and flags them for HITL review with specific guidance on what's missing
- Creates meeting folder with standard naming: `YYYY-MM-DD_Participant-Name`
- Generates v3 manifest.json with status: "ingested"
- Moves transcript to standardized `transcript.md`

#### `identify` - Calendar + CRM Enrichment
Match meeting to calendar and enrich participant data from CRM.

```bash
python3 meeting_cli.py identify <meeting-folder> [--dry-run] [--json]

# Example
python3 meeting_cli.py identify 2026-01-26_David-x-Acme/
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
python3 meeting_cli.py gate 2026-01-26_David-x-Acme/ --verbose
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

#### `process` - Canonical Shape Generation
Generate canonical meeting intelligence shapes for a gated meeting.

```bash
python3 meeting_cli.py process <meeting-folder> [--dry-run]
```

**Default behavior:**
- Routes into the **S-shape pipeline**
- Uses `run_shapes.py` + `N5/lib/meeting_shapes.py`
- Writes `manifest.shapes`
- Runs closeout/archive follow-up after successful processing

**Compatibility stance:**
- Future processing is **S-only**
- Older B-era meeting files remain readable as historical artifacts
- Any B→S adaptation should happen as a one-time migration, not through live generation flags

**Canonical shape families:**
- `S01` context
- `S02` actions / commitments / decisions
- `S03` evidence
- `S04` people
- `S05` wisdom
- `S06` recap
- `S07` Zo directives
- `S08` conditional Zo intelligence
- `PP_GRAPH_EDGES` post-processor output

#### `tick` - Orchestrated Pipeline
Process the full meeting pipeline automatically.

**Pipeline sequence:**
1. Pull / ingest new transcripts
2. Stage raw files for processing
3. Run identification pipeline on staged meetings
4. Apply quality gates with HITL escalation
5. Process gated meetings through canonical S-shape generation
6. Run closeout + archive for completed meetings

### Intake Management Commands

#### `check` - All-Points Intake Scan
Scan every meeting intake source and report what's pending or actionable.

```bash
python3 meeting_cli.py check [--verbose] [--json]
```

**Sources scanned:**
- **Local Inbox** (`Personal/Meetings/Active/`): Raw files + queued meetings by status
- **Pocket Inbox** (`Personal/Inbox/`): Unprocessed meeting-type items from Pocket webhook
- **Google Drive**: External Transcripts folders (multiple connected accounts)
- **Fathom API**: Connection health check, ready for backfill
- **Fireflies API**: Connection health check, ready for backfill

**Output:** Per-source status (OK/degraded), actionable item counts, and suggested next commands.

#### `backfill` - Historical Meeting Recovery
Pull meetings from Fathom and/or Fireflies APIs for a specific date range.

```bash
python3 meeting_cli.py backfill --source <fathom|fireflies|all> --from YYYY-MM-DD --to YYYY-MM-DD [--dry-run] [--limit N]

# Examples
python3 meeting_cli.py backfill --source all --from 2026-02-01 --to 2026-03-10 --dry-run
python3 meeting_cli.py backfill --source fireflies --from 2026-02-01 --to 2026-03-01
```

**What it does:**
- Queries the API for all recordings/transcripts in the date range
- Deduplicates against existing meetings in Inbox + archive (fuzzy title + date match)
- Converts to standard transcript.md format with speaker labels
- Drops into Inbox with `status: ingested` manifest for pipeline processing

**Requirements:** `FATHOM_API_KEY` and/or `FIREFLIES_API_KEY` set in Settings > Advanced.

#### `drive-import` - Google Drive External Transcripts
Import transcript files dropped into configured Google Drive folders.

```bash
python3 meeting_cli.py drive-import --scan [--json]    # Check for new files
python3 meeting_cli.py drive-import --pull [--dry-run]  # Pull new files into Inbox
```

**Configured folders** (in `N5/config/drive_locations.yaml`):
- `you@business-a.com` → External Transcripts (Business A)
- `you@business-b.com` → External Transcripts (Business B)

**What it does:**
- `--scan`: Lists transcript files in Drive folders, highlights files not yet imported
- `--pull`: Downloads new files to `Personal/Meetings/Active/` for pipeline processing
- Tracks imported files in `N5/data/drive_import_log.json` to avoid re-importing

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

## Canonical Shape Families

Meeting Ingestion v3 now emits a stable S-shape bundle for future meetings.

- `S01` - Context
- `S02` - Actions / commitments / decisions
- `S03` - Evidence
- `S04` - People
- `S05` - Wisdom
- `S06` - Recap
- `S07` - Zo directives
- `S08` - Conditional Zo intelligence
- `PP_GRAPH_EDGES` - Post-processor graph output

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
  "meeting_id": "2026-01-26_David-x-PartnerOrg",
  "date": "2026-01-26",
  "org": "business_a",
  "org_classification": {
    "org": "business_a",
    "confidence": 0.95,
    "signals": ["business_a", "partnership"],
    "classified_at": "2026-01-26T10:35:00Z"
  },
  "participants": [
    {"name": "David", "role": "external", "confidence": 0.95},
    {"name": "V", "role": "host", "confidence": 1.0}
  ],
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
    "event_title": "David x PartnerOrg Partnership"
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
| `routed` | Arrived via Pocket webhook (treated as ingested) | → identify |
| `identified` | Participants + calendar + CRM + org data added | → gate |
| `gated` | Quality validation passed | → process |
| `processed` | Intelligence blocks generated | → archive |
| `archived` | Moved to YYYY/MM-Month/week-NN/ folder | ✓ Complete |
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
│   ├── org_classifier.py      # Org category classification (business_a / business_b / professional / personal)
│   ├── quality_gate.py        # Quality validation (16 checks)
│   ├── process.py             # Canonical S-shape orchestration
│   ├── run_shapes.py          # Shape router + shape writers
│   ├── hitl.py                # HITL queue management
│   ├── archive.py             # Weekly folder archival
│   ├── pull.py                # Google Drive download
│   ├── stage.py               # Legacy v2 compatibility
│   ├── validate_manifest.py   # Manifest schema validation
│   └── manifest_converter.py  # v2 → v3 migration
├── references/                 # Documentation and specs  
│   ├── manifest-v3.schema.json     # JSON Schema for manifest
│   ├── meeting-id-convention.md    # Naming standards
│   ├── quality-harness-checks.md   # Quality gate specification
│   ├── hitl-queue-spec.md          # HITL queue schema
│   ├── quality-gate-docs.md        # Quality validation docs
│   └── quality-thresholds-rationale.md # Threshold rationale
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
- **Schema**: meeting_id, date, participants, type, processing metadata, archived_location

### CRM Database
Participant information storage:
- **Location**: `Personal/Knowledge/CRM/crm.db` (migrated from Legacy_Inbox)
- **Purpose**: Participant lookup, relationship classification, contact enrichment
- **Integration**: Automatic lookup during identification stage

## Typical Workflows

### Automated Processing (Every 30 Minutes)
The **Meeting Orchestrator v3** scheduled agent runs every 30 minutes using GPT 5.4:

```bash
# Agent runs:
python3 Skills/meeting-ingestion/scripts/meeting_cli.py tick --auto-process --batch-size 5
python3 Skills/meeting-ingestion/scripts/meeting_cli.py archive --execute
```

This processes the complete pipeline:
1. Ingest raw files into meeting folders  
2. Identify participants via calendar + CRM
3. Classify org category (business_a / business_b / professional / personal)
4. Validate quality and escalate to HITL if needed
5. Generate canonical meeting shapes
6. Archive completed meetings to `YYYY/MM-Month/week-NN/` folders

Processing order is LIFO (newest first) so recent meetings are prioritized over backlog.
If no pending meetings exist, the agent exits immediately.

### Manual Single Meeting Processing

```bash
# Process a specific raw transcript
cd /home/workspace
python3 Skills/meeting-ingestion/scripts/meeting_cli.py ingest transcript.md

# Continue pipeline manually  
MEETING=$(ls -1 Personal/Meetings/Active/2026-*/ | tail -1)
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

**"Shape generation failed"**
- Verify `ZO_CLIENT_IDENTITY_TOKEN` environment variable is set  
- Check if meeting passed quality gate first
- Re-run the canonical processor: `meeting_cli.py process <meeting>`

**"Calendar match confidence too low"**
- Verify Google Calendar integration is working
- Check if meeting date/time are extracted correctly from transcript
- Low confidence triggers HITL escalation for manual calendar linking

**"Meeting stuck in processing state"**
- Check manifest.json for error details
- Re-run specific pipeline stage: `meeting_cli.py process <meeting>`
- Check logs for shape generation failures

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
python3 Skills/meeting-ingestion/scripts/validate_manifest.py Personal/Meetings/Active/ --recursive
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
