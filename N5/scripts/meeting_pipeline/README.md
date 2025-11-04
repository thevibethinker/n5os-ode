# Meeting Pipeline Architecture

**Last Updated:** 2025-11-03  
**Status:** ✓ Operational with Zo orchestration

## Overview

The meeting pipeline processes transcripts from Google Drive, detects new meetings, and queues them for AI intelligence extraction.

## Architecture

### The Right Way: Zo Orchestration

The pipeline works via **scheduled task orchestration** where Zo (the AI agent) directly calls tools:

1. **Google Drive Fetch**: Zo calls `use_app_google_drive` tool directly
2. **File Processing**: Python scripts handle local file operations  
3. **Detection & Queueing**: Python scripts manage database and queue

### The Wrong Way (DEPRECATED)

❌ **DO NOT** try to make subprocess scripts call Google Drive  
❌ **DO NOT** use `pipedream_helper.py` (broken, disabled)  
❌ **DO NOT** use `gdrive_transcript_fetcher.py` (broken, disabled)

These scripts tried to call Zo tools from subprocess context, which doesn't work.

## Scheduled Task

**Task ID:** `8b833bb3-6c45-4a1a-afa9-900831c77bc5`  
**Frequency:** Every hour (active hours)  
**Approach:** Zo orchestrates tool calls + runs Python scripts

## Working Scripts

### Detection & Processing
- `transcript_processor_v4.py` - Detects new transcripts, queues for AI
- `priority_processor.py` - Handles priority meetings
- `response_handler.py` - Finalizes processed meetings
- `health_scanner.py` - System health checks

### Utilities  
- `duplicate_detector_v2.py` - Finds duplicate meetings
- `merge_meetings_v2.py` - Merges duplicate transcripts
- `block_selector.py` - Selects content blocks from meetings

## Data Flow

```
Google Drive (210 files)
    ↓ (Zo: use_app_google_drive)
Staging: N5/data/meeting_pipeline/staging/*.txt
    ↓ (Python: convert encoding, rename)
Inbox: Personal/Meetings/Inbox/*.transcript.md
    ↓ (transcript_processor_v4.py)
Database: N5/data/meeting_pipeline.db
    ↓ (queue as JSON)
AI Requests: N5/inbox/ai_requests/meeting_*.json
    ↓ (AI processing task)
Final: Personal/Meetings/{meeting_folder}/
```

## Database Schema

Location: `/home/workspace/N5/data/meeting_pipeline.db`

### Tables
- **meetings**: Meeting metadata and status
- **blocks**: Generated content blocks (B31, B32, etc.)
- **feedback**: Quality issues and corrections

### Meeting Statuses
- `detected` - Found in Inbox, not yet queued
- `queued_for_ai` - In AI processing queue
- `processing` - Currently being processed
- `complete` - All blocks generated
- `duplicate` - Marked as duplicate

## Fixing Common Issues

### Issue: "No transcripts detected"
- Check: Are files in `Personal/Meetings/Inbox/` with `.transcript.md` extension?
- Check: Are they marked `[IMPORTED-TO-ZO]`? (Should be ignored now)
- Solution: Run transcript_processor_v4.py directly

### Issue: "Google Drive download fails"  
- Check: Is the scheduled task running? (Not a subprocess script)
- Solution: Let Zo orchestrate downloads via scheduled task

### Issue: "Duplicate meetings"
- Check: Run `duplicate_detector_v2.py` to identify
- Solution: Run `merge_meetings_v2.py` to consolidate

## Files Disabled (Broken)

These files relied on subprocess→tool calls which don't work:

- `gdrive_transcript_fetcher.py.BROKEN`
- `gdrive_fetch_wrapper.py.BROKEN`  
- `gdrive_fetcher_v2.py.BROKEN`
- `pipedream_helper.py.BROKEN`

**Do not try to use or fix these.** The architecture is fundamentally wrong.

## Maintenance

### Daily
- Health scanner runs automatically (task: `76b56ced-8931-46c3-8164-ee89ae9c650b`)
- Response handler cleans up completed meetings

### Manual Operations
```bash
# Force process all Inbox transcripts
python3 /home/workspace/N5/scripts/meeting_pipeline/transcript_processor_v4.py

# Check system health
python3 /home/workspace/N5/scripts/meeting_pipeline/health_scanner.py

# Find duplicates
python3 /home/workspace/N5/scripts/meeting_pipeline/duplicate_detector_v2.py
```

## Contact

Issues? Check:
1. Scheduled task logs
2. Database status: `sqlite3 /home/workspace/N5/data/meeting_pipeline.db "SELECT status, COUNT(*) FROM meetings GROUP BY status"`
3. AI request queue: `ls /home/workspace/N5/inbox/ai_requests/meeting_*.json | wc -l`
