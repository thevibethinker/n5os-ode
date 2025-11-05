---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# Documents & Media System - Quickstart Guide

Get started with the Documents & Media Intelligence System in 5 minutes.

## Quick Commands

### 1. Auto-Scan & Process Everything
```bash
# Scan all watched directories and extract intelligence
python3 /home/workspace/N5/scripts/document_processor.py --scan && \
python3 /home/workspace/N5/scripts/intelligence_extractor.py
```

### 2. Process Single File
```bash
# Ingest and extract intelligence from one file
python3 /home/workspace/N5/scripts/document_processor.py --file /path/to/file.pdf && \
python3 /home/workspace/N5/scripts/intelligence_extractor.py
```

### 3. Check System Status
```bash
python3 /home/workspace/N5/scripts/documents_media_query.py --stats
```

## Common Workflows

### Process a Meeting Recording

```bash
# 1. Ingest the recording
python3 N5/scripts/document_processor.py --file /home/workspace/Personal/Meetings/meeting.mp4

# 2. Extract intelligence (will use transcript if available)
python3 N5/scripts/intelligence_extractor.py

# 3. View intelligence file
ls Knowledge/intelligence/media/
```

### Batch Process a Directory

```bash
# Process all documents in Reports directory
python3 N5/scripts/document_processor.py --directory /home/workspace/Reports && \
python3 N5/scripts/intelligence_extractor.py
```

### Search for Documents

```bash
# Find all documents with "strategy" in filename
python3 N5/scripts/documents_media_query.py --search "strategy"

# List all processed documents
python3 N5/scripts/documents_media_query.py --list-docs --status processed

# Get JSON output for scripting
python3 N5/scripts/documents_media_query.py --stats --format json
```

## What Gets Tracked?

**Documents:**
- PDF, Word (.docx/.doc)
- Excel (.xlsx/.xls)
- Markdown (.md), Text (.txt)
- JSON, YAML, CSV

**Media:**
- Audio: MP3, M4A, WAV
- Video: MP4, MOV, AVI
- Transcripts automatically detected

## Where Are Files?

**Database:** `/home/workspace/N5/data/documents_media.db`  
**Intelligence:** `/home/workspace/Knowledge/intelligence/`  
**Scripts:** `/home/workspace/N5/scripts/document_*.py`

## Intelligence Files

Each processed item gets an intelligence file:

**Example:** `27551f68f5529846_intelligence.md`

```markdown
---
source_id: 27551f68f5529846
source_type: document
source_file: /home/workspace/Articles/article.md
---

# Document Intelligence: article.md

## Metadata
- File Type: markdown
- Extracted: 2025-11-04

## Content Summary
- Lines: 150
- Words: 2,543
- Characters: 15,234

## Key Sections
- # Introduction
- ## Background
- ## Methodology
[...]
```

## Watched Directories

These directories are auto-scanned with `--scan`:
- `/home/workspace/Articles`
- `/home/workspace/Documents`
- `/home/workspace/Personal/Meetings`
- `/home/workspace/Records`
- `/home/workspace/Reports`

## Next Steps

1. **First Run:** Scan existing workspace
   ```bash
   python3 N5/scripts/document_processor.py --scan
   python3 N5/scripts/intelligence_extractor.py
   ```

2. **Check Results:**
   ```bash
   python3 N5/scripts/documents_media_query.py --stats
   ```

3. **Browse Intelligence:**
   ```bash
   ls -la Knowledge/intelligence/documents/
   ls -la Knowledge/intelligence/media/
   ```

4. **Set Up Automation:** (Future)
   - Scheduled task for daily scans
   - Auto-processing on file creation
   - Curation workflow integration

## Get Help

**Full Documentation:** `file 'Documents/System/DOCUMENTS_MEDIA_SYSTEM.md'`

**Architecture Spec:** `file '/home/.z/workspaces/con_tQFELbaVhzMT7EAT/WORKER_2_DELIVERABLE_DOCUMENTS_MEDIA_ARCHITECTURE.md'`

**Commands:**
```bash
# View script help
python3 N5/scripts/document_processor.py --help
python3 N5/scripts/intelligence_extractor.py --help
python3 N5/scripts/documents_media_query.py --help
```

---

*Ready to process your documents and media!*
