---
created: 2025-11-03
worker_id: 1
parent_convo: con_tZM6w5rkwiZ6ipRc
status: pending
---
# Worker Assignment: Fix Transcript Format Issue

**Parent Context:** Debugger discovered all .transcript.md files in Meeting Inbox are actually .docx format (binary Word documents). This breaks AI processing pipeline.

## Mission

Fix meeting transcript ingestion - all `.transcript.md` files are actually `.docx` format.

## Background Context

**Problem Discovered:**
- Files in `/home/workspace/Personal/Meetings/Inbox/` are named `*.transcript.md` but are Microsoft Word `.docx` files  
- AI processing pipeline expects markdown, gets binary docx data
- Root cause: Upstream ingestion from Google Drive imports wrong format

**Already Fixed:**
- Path resolution for `[IMPORTED-TO-ZO]` prefix - COMPLETE ✅
- This is a SEPARATE upstream issue

## Your Tasks

### 1. Investigate Source Process

Find and document:
- Which script downloads transcripts from Google Drive?
- How are files being imported/named?
- Where should format conversion happen?

**Hints:**
- Check `/home/workspace/N5/scripts/meeting_pipeline/` for ingestion scripts
- Look for Google Drive sync/download references
- Check scheduled tasks list for meeting import automation

### 2. One-Time Batch Conversion (REVERSIBLE)

**Safety First (P5):**
```bash
# Create timestamped backup
BACKUP_DIR="/home/workspace/Personal/Meetings/Inbox/BACKUP_DOCX_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# For each .transcript.md that's actually docx:
for file in /home/workspace/Personal/Meetings/Inbox/*.transcript.md; do
    if file "$file" | grep -q "Microsoft Word"; then
        # Backup original
        cp "$file" "$BACKUP_DIR/$(basename "$file")"
        
        # Convert docx → markdown using pandoc
        pandoc "$file" -f docx -t markdown -o "${file}.tmp"
        
        # Replace original with converted
        mv "${file}.tmp" "$file"
        
        echo "✓ Converted: $(basename "$file")"
    fi
done
```

Validate:
- Check converted files are valid markdown
- Confirm they're human-readable
- Test one file through AI processing pipeline

### 3. Fix Upstream Ingestion

**Option A (PREFERRED):** Fix at source
- Locate Google Drive download script
- Add conversion step: Download → Convert docx to markdown → Save as .transcript.md
- Test with --dry-run first

**Option B:** Add conversion layer
- Create watcher that monitors Inbox
- Auto-detect docx format files
- Auto-convert to markdown
- Register as scheduled task if needed

### 4. Set Up Ongoing Conversion (ONLY if needed)

If source cannot be fixed:
```python
# Create: N5/scripts/meeting_pipeline/auto_convert_transcripts.py

#!/usr/bin/env python3
from pathlib import Path
import subprocess
import shutil
from datetime import datetime

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

for file in INBOX.glob("*.transcript.md"):
    # Check if docx
    result = subprocess.run(['file', str(file)], capture_output=True, text=True)
    if "Microsoft Word" in result.stdout:
        # Backup
        backup_dir = INBOX / f"BACKUP_{datetime.now():%Y%m%d}"
        backup_dir.mkdir(exist_ok=True)
        shutil.copy(file, backup_dir / file.name)
        
        # Convert
        subprocess.run(['pandoc', str(file), '-f', 'docx', '-t', 'markdown', '-o', f"{file}.tmp"])
        file.unlink()
        Path(f"{file}.tmp").rename(file)
        
        print(f"✓ Converted: {file.name}")
```

### 5. Validation & Report

**Verify:**
- Converted files are valid markdown
- AI processing can read them
- Test one file end-to-end through meeting pipeline

**Document:**
- What was the source issue?
- How was it fixed?
- Where are backups stored?
- Is ongoing conversion needed?

**Create Report:**
`/home/workspace/N5/runtime/transcript_format_fix_$(date +%Y%m%d).md`

Include:
- Problem description
- Investigation findings
- Solution implemented
- Backup locations
- Reversal instructions
- Validation results

## Safety Requirements (P5)

- ✅ All originals backed up before conversion
- ✅ Fully reversible process documented
- ✅ Test with one file before batch processing
- ✅ Document backup locations clearly

## Success Criteria

- ✅ Source issue identified and documented
- ✅ All existing files converted (with timestamped backups)
- ✅ Upstream process fixed OR ongoing conversion active
- ✅ Validation: AI processing works on converted files  
- ✅ Complete documentation with reversal steps

## Deliverables

1. Investigation report on source process
2. Batch conversion completion (with backup confirmation)
3. Upstream fix implemented OR ongoing conversion script
4. End-to-end validation test results
5. Comprehensive fix report in N5/runtime/

## Reversal Instructions

If anything goes wrong:
```bash
# Restore originals from backup
cp BACKUP_DOCX_YYYYMMDD_HHMMSS/* /home/workspace/Personal/Meetings/Inbox/
```

Backup paths will be documented in your final report.

---

**Next Step:** Open this file in a NEW conversation and begin work.
