# Meeting Processing V3 Architecture

**Version**: 3.0.0  
**Last Updated**: 2025-10-12  
**Status**: ✅ Active

---

## Overview

The Meeting Processing system automatically detects, downloads, and processes meeting transcripts from Google Drive, generating comprehensive "Smart Blocks" of meeting intelligence.

## System Components

### 1. Auto-Detection (Every 30 minutes)
**Scheduled Task**: `meeting-transcript-scan`  
**Script**: Auto-processor logic in scheduled task

**What it does:**
- Scans Google Drive folder for new transcripts
- Creates processing request JSONs in `N5/inbox/meeting_requests/`
- Deduplicates based on gdrive_id to prevent reprocessing
- Classifies stakeholders as internal or external

### 2. Auto-Processing (Every 10 minutes)
**Scheduled Task**: `📝 Meeting Transcript Processing`  
**Event ID**: `4cb2fde2-2900-47d7-9040-fdf26cb4db62`  
**Model**: Claude Sonnet 4.5

**What it does:**
- Checks for pending requests in `N5/inbox/meeting_requests/`
- Processes ONLY ONE transcript per run (FIFO ordering)
- Downloads transcript from Google Drive
- Uses `TemplateManager` to load appropriate templates
- Generates Smart Blocks via native LLM analysis
- Saves blocks to meeting directory
- Marks Google Drive file as `[ZO-PROCESSED]`
- Moves request to `processed/` folder

### 3. Template Management
**Script**: `N5/scripts/meeting_intelligence_orchestrator.py`  
**Class**: `TemplateManager`

**What it provides:**
- Template loading based on classification (internal/external)
- Block definition registry
- Essential links injection
- Meeting directory structure management

### 4. Smart Blocks Output

#### Internal Meeting Blocks
Priority blocks generated for internal strategy sessions:

| Block | Name | Priority | Purpose |
|-------|------|----------|---------|
| B01 | Detailed Recap | Required | Key decisions and agreements |
| B08 | Resonance Points | Required | Moments of connection |
| B21 | Salient Questions | High | Strategic questions raised |
| B22 | Debate/Tension Analysis | High | Areas of disagreement |
| B24 | Product Idea Extraction | Conditional | Product/feature ideas |
| B29 | Key Quotes | Medium | Significant verbatim quotes |

#### External Meeting Blocks
Priority blocks generated for external stakeholder meetings:

| Block | Name | Priority | Purpose |
|-------|------|----------|---------|
| B01 | Detailed Recap | Required | Key decisions and agreements |
| B08 | Resonance Points | Required | Moments of connection |
| B21 | Salient Questions | High | Strategic questions raised |
| B25 | Deliverable Content Map | High | Promised deliverables |
| B28 | Founder Profile | External Only | Founder/company profile |
| B14 | Blurbs Requested | Medium | Intro blurbs for warm intros |
| B30 | Intro Email Template | Conditional | Introduction email template |

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DETECTION (Every 30 min)                                     │
│    Google Drive Folder Scan → New Transcripts Detected          │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. REQUEST CREATION                                              │
│    Create JSON in N5/inbox/meeting_requests/{meeting-id}_*.json │
│    Contains: gdrive_id, classification, participants, metadata   │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. PROCESSING (Every 10 min, ONE at a time)                     │
│    - Zo loads oldest request (FIFO)                             │
│    - Downloads transcript from Google Drive                      │
│    - Initializes TemplateManager                                 │
│    - Generates Smart Blocks                                      │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. OUTPUT STORAGE                                                │
│    N5/records/meetings/{meeting_id}/                             │
│    ├── B01_detailed_recap.md                                     │
│    ├── B08_resonance_points.md                                   │
│    ├── B21_salient_questions.md                                  │
│    ├── ... (other blocks)                                        │
│    └── _metadata.json                                            │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. FINALIZATION                                                  │
│    - Mark Google Drive file: [ZO-PROCESSED] prefix              │
│    - Move request: processed/ folder                             │
│    - Ready for downstream consumption                            │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
N5/
├── inbox/
│   ├── meeting_requests/              # Pending processing requests
│   │   ├── {meeting-id}_request.json
│   │   └── processed/                 # Completed requests (archived)
│   └── transcripts/                   # Downloaded transcripts
│       └── {meeting-id}.txt
├── records/
│   └── meetings/
│       └── {meeting-id}/              # Meeting intelligence output
│           ├── B01_detailed_recap.md
│           ├── B08_resonance_points.md
│           ├── ... (other blocks)
│           └── _metadata.json
├── prefs/
│   └── block_templates/
│       ├── internal/                  # Templates for internal meetings
│       │   ├── B01.template.md
│       │   └── ...
│       └── external/                  # Templates for external meetings
│           ├── B01.template.md
│           └── ...
└── scripts/
    └── meeting_intelligence_orchestrator.py  # TemplateManager
```

## Key Design Decisions

### Why One Transcript Per Run?
- **Context Window Management**: Prevents overflow with long transcripts
- **Predictable Performance**: Consistent processing time and resource usage
- **Error Isolation**: Failure in one transcript doesn't block others
- **Quality Focus**: Full attention to each meeting's analysis

### Why FIFO Ordering?
- **Temporal Relevance**: Older meetings processed first
- **Fair Processing**: No cherry-picking or skipping
- **Predictable Queue**: V can estimate when meetings will be processed

### Why Template-Guided?
- **Consistency**: Same structure across all meetings
- **Customization**: Different templates for internal vs external
- **Efficiency**: Zo knows exactly what to extract
- **Maintainability**: Templates can be updated without code changes

## Related Commands

### Primary Commands
- `command 'meeting-process'` - Process next pending transcript
- `command 'meeting-intelligence-orchestrator'` (alias: `mio`) - Direct invocation

### Downstream Commands
- `command 'meeting-approve'` - Review and approve generated blocks
- `command 'deliverable-generate'` - Create deliverables from blocks
- `command 'follow-up-email-generator'` - Draft follow-up emails

### Upstream Commands
- `command 'transcript-ingest'` - Manual transcript ingestion
- `command 'meeting-transcript-scan'` - Auto-detection (scheduled)

## Monitoring & Debugging

### Check Processing Queue
```bash
ls -lt N5/inbox/meeting_requests/*.json | head -5
```

### Check Processed Meetings
```bash
ls -lt N5/records/meetings/
```

### View Scheduled Task Status
Navigate to: https://va.zo.computer/schedule

### Check Template Manager Logs
```bash
ls -lt N5/logs/template_manager_*.log | head -5
tail -f N5/logs/template_manager_{meeting-id}.log
```

## Troubleshooting

### No transcripts being processed?
1. Check if requests exist: `ls N5/inbox/meeting_requests/*.json`
2. Verify scheduled task is active: Check Zo schedule page
3. Check logs: `N5/logs/template_manager_*.log`

### Blocks not generating correctly?
1. Verify templates exist: `ls N5/prefs/block_templates/{internal,external}/`
2. Check classification in request JSON
3. Review TemplateManager logs

### Google Drive connection issues?
1. Verify Google Drive app is connected
2. Check gdrive_id in request JSON is valid
3. Ensure transcript file exists in Google Drive

## Version History

- **v1.0** (deprecated): Original `meeting_orchestrator.py` with subprocess LLM calls
- **v2.0** (deprecated): Phased workflow with Python-based extraction
- **v3.0** (current): TemplateManager + Zo native LLM processing

## Future Enhancements

See `file 'Lists/system-upgrades.jsonl'` for planned improvements:
- Howie ↔ Zo post-meeting automation pipeline
- Auto-generated follow-up emails
- CRM integration
- Meeting analytics dashboard
