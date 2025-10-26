# Meeting Queue Protocol

**Version**: 2.0  
**Last Updated**: 2025-10-11  
**Status**: Active

## Overview

This protocol governs the meeting transcript ingestion workflow, from Google Drive scan to processing queue management. It ensures zero duplicates, consistent naming, and proper classification.

---

## Naming Convention

### Standard Format

**Internal Meetings:**
```
YYYY-MM-DD_internal-team[-HHMMSS]
```

**External Meetings:**
```
YYYY-MM-DD_external-{participant-slug}[-HHMMSS]
```

### Time Suffix Rules
- **Optional** time suffix `HHMMSS` added ONLY when multiple meetings of same type occur on same day
- Time extracted from original filename timestamp
- Example: `2025-09-23_internal-team-143803` (second internal meeting that day)

### Examples

| Original Filename | Classification | Meeting ID |
|-------------------|----------------|------------|
| `Daily team stand-up-transcript-2025-10-03T14-15-16.277Z.docx` | Internal | `2025-10-03_internal-team` |
| `Alex x Vrijen - Wisdom Partners Coaching-transcript-2025-10-09T18-06-05.257Z.docx` | External | `2025-10-09_external-alex-wisdom-partners-coaching` |
| `Stephanie x Vrijen-transcript-2025-09-23T14-11-04.483Z.docx` | External | `2025-09-23_external-stephanie` |
| `Daily team stand-up-transcript-2025-09-23T14-38-03.060Z.docx` (2nd that day) | Internal | `2025-09-23_internal-team-143803` |

---

## Classification Rules

### Internal Meeting Indicators

A meeting is classified as **internal** if:

1. **Filename contains internal keywords:**
   - "daily team stand-up"
   - "team standup"  
   - "co-founder"
   - "extended cof"
   - "bi-weekly extended"
   - "internal"

2. **Transcript analysis** (fallback):
   - Email domains only contain: `@mycareerspan.com`, `@theapply.ai`
   - No external participant emails found

### External Meeting Classification

A meeting is classified as **external** if NOT internal.

**Participant Extraction:**
1. Remove Careerspan team references:
   - "x Vrijen"
   - "and Vrijen Attawar"
   - "+ Logan Currie"
2. Remove transcript suffixes: "-transcript-", "transcript"
3. Slugify: lowercase, replace special chars/spaces with `-`

**Examples:**
- "Alex x Vrijen - Wisdom Partners Coaching" → `alex-wisdom-partners-coaching`
- "Giovanna Ventola and Vrijen Attawar + Logan Currie" → `giovanna-ventola`
- "Stephanie x Vrijen" → `stephanie`

---

## Deduplication Strategy

### Multi-Layer Check

Before creating ANY new request, check these locations for existing `gdrive_id`:

1. **Pending Queue**: `N5/inbox/meeting_requests/*_request.json`
2. **Completed**: `N5/inbox/meeting_requests/completed/*_request.json`
3. **Processed**: `N5/inbox/meeting_requests/processed/*_request.json`
4. **Meeting Folders**: `N5/records/meetings/*/_metadata.json`

### Skip Criteria

**SKIP file if:**
- Filename starts with `[ZO-PROCESSED]` prefix (Google Drive state marker)
- `gdrive_id` found in any of the above locations
- File already has a pending or completed request

### Duplicate Detection Results (Current)

As of 2025-10-11 cleanup:
- **Before**: 40 pending requests (23 duplicates)
- **After**: 17 unique requests (0 duplicates)
- **Verified**: No gdrive_id appears more than once

---

## File Organization

### Directory Structure

```
N5/inbox/
├── transcripts/           # Downloaded .txt transcripts
│   └── {meeting-id}.txt
└── meeting_requests/      # Processing queue
    ├── {meeting-id}_request.json
    ├── completed/         # Successfully processed
    ├── processed/         # Archived after completion
    └── failed/            # Failed processing attempts

N5/records/meetings/       # Processed meeting folders (PRIMARY LOCATION)
└── {meeting-id}/
    ├── _metadata.json     # Contains gdrive_id
    ├── transcript.txt
    ├── blocks.md
    └── ...

Careerspan/Meetings/       # Symlink to N5/records/meetings (for compatibility)
└── → ../N5/records/meetings/
```

### Request File Format

```json
{
  "meeting_id": "2025-10-10_external-alex-wisdom-partners-coaching",
  "classification": "external",
  "external_participant": "alex-wisdom-partners-coaching",
  "participants": "Alex x Vrijen - Wisdom Partners Coaching",
  "date": "2025-10-10",
  "time_suffix": "180605",
  "gdrive_id": "1abc123...",
  "gdrive_link": "https://docs.google.com/document/d/...",
  "original_filename": "Alex x Vrijen-transcript-2025-10-10T18-06-05.257Z.docx",
  "created_at": "2025-10-11T03:45:00.000000Z",
  "status": "pending"
}
```

**Required Fields:**
- `meeting_id` - Standardized ID per naming convention
- `classification` - "internal" or "external"
- `date` - YYYY-MM-DD
- `gdrive_id` - Unique identifier for deduplication
- `gdrive_link` - Link to original file
- `original_filename` - Original Google Drive filename
- `status` - "pending", "processing", "completed", "failed"

**Optional Fields:**
- `external_participant` - Slug for external meetings only
- `time_suffix` - HHMMSS when multiple same-day meetings
- `participants` - Original participant string (for reference)

---

## Scheduled Task Configuration

### Current Task
- **Event ID**: `afda82fa-7096-442a-9d65-24d831e3df4f`
- **Command**: `meeting-transcript-scan`
- **Schedule**: (TBD - check via `list_scheduled_tasks`)

### Task Instruction

```
Execute command 'meeting-transcript-scan' from file 'N5/commands/meeting-transcript-scan.md'.

CRITICAL DEDUPLICATION REQUIREMENTS:
1. Before processing ANY transcript, load ALL existing gdrive_ids from:
   - N5/inbox/meeting_requests/*.json
   - N5/inbox/meeting_requests/completed/*.json  
   - N5/inbox/meeting_requests/processed/*.json
   - N5/records/meetings/*/_metadata.json

2. SKIP any file whose gdrive_id already exists in the system

3. Use naming convention:
   - Internal: YYYY-MM-DD_internal-team
   - External: YYYY-MM-DD_external-{name}

4. Only create requests for NEW transcripts not in queue or processed
```

---

## Verification Commands

### Check Queue Status
```bash
# Count pending requests
ls -1 N5/inbox/meeting_requests/*_request.json | wc -l

# List by classification
ls -1 N5/inbox/meeting_requests/*internal* | wc -l
ls -1 N5/inbox/meeting_requests/*external* | wc -l
```

### Check for Duplicates
```bash
python3 << 'PY'
import json
from pathlib import Path
from collections import Counter

req_dir = Path('N5/inbox/meeting_requests')
gdrive_ids = []

for fpath in req_dir.glob('*_request.json'):
    with open(fpath) as f:
        data = json.load(f)
        if gid := data.get('gdrive_id'):
            gdrive_ids.append(gid)

dupes = {k: v for k, v in Counter(gdrive_ids).items() if v > 1}
print(f"Duplicates: {len(dupes)}")
for gid, count in dupes.items():
    print(f"  {gid}: {count} copies")
PY
```

### Verify Naming Convention
```bash
# Should return 0 (no files violate convention)
ls -1 N5/inbox/meeting_requests/*_request.json | \
  grep -v -E '20[0-9]{2}-[0-9]{2}-[0-9]{2}_(internal-team|external-[a-z0-9-]+)(_request\.json|.*_request\.json)$' | \
  wc -l
```

---

## Maintenance

### Cleanup Commands

**Remove Duplicates:**
```bash
python3 N5/scripts/n5_meeting_request_deduplicator.py
```

**Standardize Names:**
```bash
python3 N5/scripts/n5_meeting_request_standardizer.py
```

**Verify System Integrity:**
```bash
# Check for orphaned transcripts
find N5/inbox/transcripts -name "*.txt" -type f | wc -l

# Check processed meetings
ls -1d N5/records/meetings/*/ | wc -l
```

### Regular Audits

**Weekly:**
- Check for duplicate gdrive_ids
- Verify naming convention compliance
- Review failed requests

**Monthly:**
- Archive old completed requests
- Clean up orphaned transcripts
- Update classification rules if needed

---

## Error Recovery

### Duplicate Request Created

**Symptom:** Same gdrive_id appears in multiple requests

**Resolution:**
1. Run deduplicator script
2. Manually verify which is most recent
3. Delete older versions
4. Check scheduled task is using latest instruction

### Missing Transcript

**Symptom:** Request exists but no transcript file

**Resolution:**
1. Re-download from Google Drive using gdrive_id
2. Convert to text via pandoc
3. Update request status

### Wrong Classification

**Symptom:** Internal meeting labeled external (or vice versa)

**Resolution:**
1. Edit request JSON: update `classification` field
2. Rename file to match convention
3. Update `meeting_id` if needed
4. Consider adding keyword to classification rules

---

## Related Documentation

- `file 'N5/commands/meeting-transcript-scan.md'` - Scanner command spec
- `file 'N5/scripts/n5_meeting_request_standardizer.py'` - Standardization tool
- `file 'N5/scripts/n5_meeting_transcript_scanner.py'` - Core scanner logic

---

## Change Log

### 2025-10-11 - v2.0 (This Update)
- **Added**: Comprehensive deduplication across all locations
- **Added**: Consistent naming convention (internal/external)
- **Added**: Time suffix for same-day meetings
- **Fixed**: Removed 23 duplicate requests (40 → 17)
- **Fixed**: Standardized all meeting_ids
- **Updated**: Scheduled task instruction with deduplication requirements

### Prior - v1.x
- Initial queuing system
- Basic Google Drive scanning
- Manual processing workflow
