---
created: 2026-02-09
last_edited: 2026-02-09  
version: 1.0
provenance: con_EHo97McpEpE09T3Z
---

# Meeting Ingestion CLI Reference

Quick reference for all Meeting Ingestion v3 command-line operations.

## Main CLI: meeting_cli.py

**Location:** `Skills/meeting-ingestion/scripts/meeting_cli.py`

### v3 Pipeline Commands

#### ingest - Convert Raw → Ingested
```bash
python3 meeting_cli.py ingest <path> [OPTIONS]

OPTIONS:
  --dry-run          Preview without making changes
  --json             Output JSON format
  --priority LEVEL   Set processing priority (urgent|normal|low)

EXAMPLES:
  python3 meeting_cli.py ingest transcript.md
  python3 meeting_cli.py ingest meeting-folder/ --dry-run
  python3 meeting_cli.py ingest . --json  # Process all in current directory
```

#### identify - Calendar + CRM Enrichment  
```bash
python3 meeting_cli.py identify <meeting-folder> [OPTIONS]

OPTIONS:
  --dry-run          Preview identification without updating manifest
  --json             Output JSON format
  --force-calendar   Bypass calendar cache, force fresh API call
  --skip-crm         Skip CRM enrichment (identification only)

EXAMPLES:
  python3 meeting_cli.py identify 2026-02-09_Alice-x-Strategy/
  python3 meeting_cli.py identify 2026-02-09_Alice-x-Strategy/ --dry-run --json
  python3 meeting_cli.py identify 2026-02-09_Alice-x-Strategy/ --force-calendar
```

#### gate - Quality Validation
```bash
python3 meeting_cli.py gate <meeting-folder> [OPTIONS]

OPTIONS:
  --dry-run          Preview quality checks without updating manifest
  --verbose          Show detailed check results  
  --json             Output JSON format
  --config FILE      Use custom quality config file
  --bypass REASON    Emergency bypass (use with caution)

EXAMPLES:
  python3 meeting_cli.py gate 2026-02-09_Alice-x-Strategy/
  python3 meeting_cli.py gate 2026-02-09_Alice-x-Strategy/ --verbose
  python3 meeting_cli.py gate 2026-02-09_Alice-x-Strategy/ --bypass "urgent-processing"
```

#### process - Block Generation
```bash
python3 meeting_cli.py process <meeting-folder> [OPTIONS]

OPTIONS:
  --blocks LIST      Comma-separated block list (B01,B05,B08)
  --dry-run          Preview block selection without generating
  --recipe NAME      Use specific recipe (external_standard, internal_standup, etc.)
  --priority FOCUS   Weight selection toward priority (business|career|personal)
  --skip-smart       Skip smart selector, use recipe defaults only

EXAMPLES:
  python3 meeting_cli.py process 2026-02-09_Alice-x-Strategy/  # Smart selection
  python3 meeting_cli.py process 2026-02-09_Alice-x-Strategy/ --blocks B01,B05,B08
  python3 meeting_cli.py process 2026-02-09_Alice-x-Strategy/ --recipe external_sales
  python3 meeting_cli.py process 2026-02-09_Alice-x-Strategy/ --priority business
```

#### tick - Orchestrated Pipeline
```bash
python3 meeting_cli.py tick [OPTIONS]

OPTIONS:
  --dry-run          Preview entire pipeline without making changes
  --batch-size N     Max meetings to process (default: 5)
  --stage STAGE      Run specific stage only (ingest|identify|gate|process|archive)
  --priority LEVEL   Process only meetings with priority level
  --timeout SECONDS  Max time per stage (default: 300)

EXAMPLES:
  python3 meeting_cli.py tick                    # Full pipeline
  python3 meeting_cli.py tick --dry-run          # Preview
  python3 meeting_cli.py tick --batch-size 10    # Larger batch
  python3 meeting_cli.py tick --stage process    # Process stage only
```

### Legacy Commands (v2 Compatibility)

#### status - Pipeline Overview
```bash
python3 meeting_cli.py status [OPTIONS]

OPTIONS:
  --detailed         Show individual meeting details
  --json             Output JSON format
  --stage STAGE      Filter by pipeline stage
  --age HOURS        Show meetings older than N hours
  --problems-only    Show only meetings with issues

EXAMPLES:
  python3 meeting_cli.py status                  # Overview
  python3 meeting_cli.py status --detailed       # Individual meetings  
  python3 meeting_cli.py status --problems-only  # Issues only
  python3 meeting_cli.py status --stage gated    # Show gated meetings
```

#### archive - Move to Weekly Folders
```bash
python3 meeting_cli.py archive [OPTIONS]

OPTIONS:
  --execute          Actually move meetings (default: preview only)
  --batch-size N     Max meetings to archive (default: 20)
  --force            Override collision detection
  --weeks N          Archive meetings from last N weeks
  --verify           Check archive integrity after move

EXAMPLES:
  python3 meeting_cli.py archive                 # Preview
  python3 meeting_cli.py archive --execute       # Execute  
  python3 meeting_cli.py archive --execute --verify
  python3 meeting_cli.py archive --weeks 2 --execute
```

#### stage - Legacy v2 Staging
```bash
python3 meeting_cli.py stage [OPTIONS]

OPTIONS:
  --dry-run          Preview without making changes
  --quarantine       Move orphaned files to quarantine
  --suffix-mode      Use v2 suffix mode for compatibility

EXAMPLES:
  python3 meeting_cli.py stage                   # Convert raw files
  python3 meeting_cli.py stage --quarantine      # Clean up orphans
```

#### fix - Repair Pipeline State  
```bash
python3 meeting_cli.py fix [OPTIONS]

OPTIONS:
  --dry-run          Preview repairs without making changes
  --quarantine-only  Only move orphaned files
  --reset-failed     Reset failed meetings to previous stage
  --rebuild-manifests Regenerate corrupted manifests

EXAMPLES:  
  python3 meeting_cli.py fix                     # Full repair
  python3 meeting_cli.py fix --quarantine-only   # Clean orphans only
  python3 meeting_cli.py fix --reset-failed      # Reset failures
```

### Advanced Commands

#### stats - Statistics and Analytics
```bash
python3 meeting_cli.py stats [OPTIONS]

OPTIONS:
  --period PERIOD    Time period (day|week|month|quarter|year)
  --export FILE      Export to JSON file
  --breakdown        Show detailed breakdown
  --compare-baseline Compare to performance baseline

EXAMPLES:
  python3 meeting_cli.py stats --period week
  python3 meeting_cli.py stats --breakdown --export /tmp/stats.json
  python3 meeting_cli.py stats --compare-baseline
```

#### health-check - System Health
```bash
python3 meeting_cli.py health-check [OPTIONS]

OPTIONS:
  --full             Run comprehensive health check
  --config FILE      Use custom health check config
  --alert            Send alerts for critical issues
  --report FILE      Save health report to file

EXAMPLES:
  python3 meeting_cli.py health-check           # Basic check
  python3 meeting_cli.py health-check --full    # Comprehensive
  python3 meeting_cli.py health-check --alert --report /tmp/health.txt
```

#### benchmark - Performance Testing
```bash
python3 meeting_cli.py benchmark [OPTIONS]

OPTIONS:
  --establish-baseline Create new performance baseline
  --compare-to-baseline Compare current performance
  --batch-sizes LIST   Test different batch sizes (1,5,10,20)
  --export FILE        Export results to JSON

EXAMPLES:
  python3 meeting_cli.py benchmark --establish-baseline
  python3 meeting_cli.py benchmark --batch-sizes 1,3,5,10
  python3 meeting_cli.py benchmark --compare-to-baseline --alert-threshold 25%
```

---

## Supporting CLIs

### Block Selector: block_selector.py

**Purpose:** Intelligent block selection for meetings

```bash
python3 block_selector.py <meeting-folder> [OPTIONS]

OPTIONS:
  --dry-run          Show recipe without LLM analysis
  --json             Output JSON format
  --recipe RECIPE    Force specific recipe
  --debug            Show detailed selection reasoning
  --priorities LIST  Override priority focus (business,career,personal)

EXAMPLES:
  python3 block_selector.py 2026-02-09_Alice-x-Strategy/
  python3 block_selector.py 2026-02-09_Alice-x-Strategy/ --dry-run --json
  python3 block_selector.py 2026-02-09_Alice-x-Strategy/ --debug
  python3 block_selector.py 2026-02-09_Alice-x-Strategy/ --priorities business,career
```

### Block Generator: block_generator.py

**Purpose:** LLM-powered block generation

```bash
python3 block_generator.py <meeting-folder> [OPTIONS]

OPTIONS:
  --blocks LIST      Generate specific blocks only
  --dry-run          Preview without generating files
  --test-api         Test Zo API connectivity
  --validate-prompts Check prompt file integrity
  --timing-report    Show generation timing analysis
  --retry-failures   Retry previously failed blocks

EXAMPLES:
  python3 block_generator.py 2026-02-09_Alice-x-Strategy/
  python3 block_generator.py 2026-02-09_Alice-x-Strategy/ --blocks B01,B05
  python3 block_generator.py 2026-02-09_Alice-x-Strategy/ --retry-failures
  python3 block_generator.py --test-api
```

### Quality Gate: quality_gate.py

**Purpose:** Meeting quality validation

```bash
python3 quality_gate.py <manifest.json> [OPTIONS]

OPTIONS:
  --transcript FILE  Specify transcript file location  
  --verbose          Show detailed check results
  --json             Output JSON format
  --config FILE      Use custom quality config
  --check-by-check   Run checks individually
  --stats PERIOD     Show quality statistics (day|week|month)

EXAMPLES:
  python3 quality_gate.py meeting/manifest.json --transcript meeting/transcript.md
  python3 quality_gate.py meeting/manifest.json --verbose
  python3 quality_gate.py meeting/manifest.json --check-by-check
  python3 quality_gate.py --stats week
```

### HITL Queue: hitl.py

**Purpose:** Human-in-the-loop queue management

```bash
python3 hitl.py COMMAND [OPTIONS]

COMMANDS:
  status             Show queue status
  process ID         Process specific HITL item
  resolve ID         Resolve HITL item with data
  batch-process      Process multiple items
  cleanup            Remove old/resolved items
  auto-resolve       Auto-resolve high-confidence items

STATUS OPTIONS:
  --priority P0|P1|P2  Filter by priority level
  --age HOURS          Show items older than N hours  
  --summary            Show summary only
  --json               Output JSON format

EXAMPLES:
  python3 hitl.py status
  python3 hitl.py status --priority P1 --summary
  python3 hitl.py process HITL-20260209-001
  python3 hitl.py resolve HITL-20260209-001 --participant "Alice Smith"
  python3 hitl.py cleanup --older-than 7d
  python3 hitl.py auto-resolve --confidence-threshold 0.9
```

### Calendar Match: calendar_match.py

**Purpose:** Google Calendar triangulation

```bash
python3 calendar_match.py COMMAND [OPTIONS]

COMMANDS:
  match MANIFEST     Match meeting to calendar
  search             Search calendar events
  test-connection    Test Google Calendar API
  cache-refresh      Refresh calendar cache
  quota-status       Check API quota usage

EXAMPLES:
  python3 calendar_match.py match meeting/manifest.json
  python3 calendar_match.py search --date 2026-02-09 --keywords "strategy meeting"
  python3 calendar_match.py test-connection
  python3 calendar_match.py cache-refresh --days 7
  python3 calendar_match.py quota-status
```

### CRM Enricher: crm_enricher.py

**Purpose:** Participant data enrichment

```bash
python3 crm_enricher.py COMMAND [OPTIONS]

COMMANDS:
  enrich MANIFEST    Enrich meeting participants from CRM
  add-participant    Add new participant to CRM  
  lookup NAME        Look up participant details
  cleanup            Clean up CRM database
  rebuild            Rebuild CRM from manifests

EXAMPLES:
  python3 crm_enricher.py enrich meeting/manifest.json
  python3 crm_enricher.py add-participant "Alice Smith" --company "TechCorp" --role external
  python3 crm_enricher.py lookup "Alice Smith"
  python3 crm_enricher.py cleanup --remove-orphans --merge-duplicates
  python3 crm_enricher.py rebuild --from-manifests Personal/Meetings/
```

### Transcript Ingestor: ingest.py

**Purpose:** Raw transcript processing

```bash
python3 ingest.py COMMAND <path> [OPTIONS]

COMMANDS:
  ingest-file FILE   Process single file
  ingest-folder DIR  Process folder containing transcript
  test-extraction    Test participant/metadata extraction

OPTIONS:
  --dry-run          Preview without creating files
  --format FORMAT    Force format detection (jsonl|markdown|folder)
  --output-dir DIR   Specify output directory

EXAMPLES:
  python3 ingest.py ingest-file transcript.md
  python3 ingest.py ingest-folder meeting-folder/
  python3 ingest.py test-extraction transcript.md --verbose
```

### Archive Manager: archive.py

**Purpose:** Weekly folder archival

```bash
python3 archive.py [OPTIONS]

OPTIONS:
  --execute          Actually archive meetings (default: preview)
  --meeting FOLDER   Archive specific meeting
  --weeks N          Archive from last N weeks
  --verify           Verify archive integrity
  --check-collisions Check for naming collisions
  --resolve-collisions Resolve collisions with suffix

EXAMPLES:
  python3 archive.py                            # Preview
  python3 archive.py --execute                  # Execute
  python3 archive.py --meeting 2026-02-09_Alice-x-Strategy/
  python3 archive.py --check-collisions --weeks 4
  python3 archive.py --resolve-collisions --suffix-strategy
```

### Drive Puller: pull.py

**Purpose:** Google Drive download

```bash
python3 pull.py [OPTIONS]

OPTIONS:
  --dry-run          Preview without downloading
  --batch-size N     Max files to download (default: 10)
  --format FILTER    Download specific formats only (md|jsonl|all)
  --quota-status     Check Drive API quota usage

EXAMPLES:
  python3 pull.py                               # Standard pull
  python3 pull.py --dry-run --batch-size 20     # Preview large batch
  python3 pull.py --format md                   # Markdown only
  python3 pull.py --quota-status                # Check quotas
```

### Manifest Validator: validate_manifest.py

**Purpose:** Manifest schema validation

```bash
python3 validate_manifest.py <target> [OPTIONS]

TARGET:
  FILE               Validate single manifest.json
  DIRECTORY          Validate all manifests in directory

OPTIONS:
  --recursive        Scan subdirectories
  --fix-minor        Automatically fix minor issues
  --schema FILE      Use custom schema file
  --export-errors    Export validation errors to JSON
  --reset-to STAGE   Reset meeting to earlier pipeline stage

EXAMPLES:
  python3 validate_manifest.py meeting/manifest.json
  python3 validate_manifest.py Personal/Meetings/Inbox/ --recursive
  python3 validate_manifest.py meeting/manifest.json --fix-minor
  python3 validate_manifest.py meeting/manifest.json --reset-to identified
```

---

## Common Command Patterns

### Full Pipeline for New Transcript
```bash
# Automated (recommended)
python3 meeting_cli.py tick

# Manual step-by-step
python3 meeting_cli.py ingest transcript.md
MEETING=$(ls -1 Personal/Meetings/Inbox/2026-*/ | tail -1)
python3 meeting_cli.py identify "$MEETING"
python3 meeting_cli.py gate "$MEETING"
python3 meeting_cli.py process "$MEETING"
python3 meeting_cli.py archive --execute
```

### Emergency Processing (Bypass Quality Gate)
```bash
python3 meeting_cli.py ingest urgent-transcript.md --priority urgent
MEETING=$(ls -1 Personal/Meetings/Inbox/2026-*/ | tail -1)
python3 meeting_cli.py identify "$MEETING"
python3 meeting_cli.py gate "$MEETING" --bypass "urgent-processing"  
python3 meeting_cli.py process "$MEETING" --blocks B01,B05,B08
python3 meeting_cli.py archive --execute --force
```

### HITL Queue Processing
```bash
# Daily HITL review
python3 hitl.py status --summary
python3 hitl.py batch-process --priority P1 --limit 5
python3 hitl.py auto-resolve --confidence-threshold 0.85

# Weekly cleanup
python3 hitl.py cleanup --older-than 7d
python3 hitl.py archive --older-than 30d
```

### System Maintenance
```bash
# Daily health check
python3 meeting_cli.py health-check --alert

# Weekly maintenance
python3 meeting_cli.py stats --period week --export stats.json
python3 crm_enricher.py cleanup --remove-orphans
python3 archive.py --verify --weeks 4

# Monthly optimization
python3 meeting_cli.py benchmark --compare-to-baseline --alert-threshold 20%
sqlite3 Personal/Knowledge/CRM/crm.db "VACUUM; ANALYZE;"
sqlite3 N5/data/meeting_registry.db "VACUUM; ANALYZE;"
```

### Troubleshooting Workflows
```bash
# Diagnose stuck pipeline
python3 meeting_cli.py status --problems-only --detailed
python3 meeting_cli.py health-check --full --report /tmp/diagnosis.txt

# Reset failed meeting  
python3 validate_manifest.py meeting/manifest.json --reset-to ingested
python3 meeting_cli.py identify meeting/ --force-calendar

# Test system components
python3 calendar_match.py test-connection
python3 block_generator.py --test-api
python3 quality_gate.py --self-test
```

---

## Exit Codes

All CLI tools use standard exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Permission denied |
| 5 | API failure |
| 6 | Quality gate failure |
| 7 | HITL escalation required |
| 8 | Database error |
| 9 | Timeout |
| 10 | Insufficient resources |

---

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `ZO_CLIENT_IDENTITY_TOKEN` | Zo API authentication | Yes |
| `GOOGLE_CALENDAR_CREDENTIALS` | Calendar API access | Yes |
| `MEETING_DEBUG` | Enable debug logging | No |
| `MEETING_BATCH_SIZE` | Default batch size | No |
| `MEETING_TIMEOUT` | Default timeout (seconds) | No |

---

*Meeting Ingestion CLI Reference v1.0 | February 2026*