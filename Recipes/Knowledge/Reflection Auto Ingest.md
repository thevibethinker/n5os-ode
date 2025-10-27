---
description: 'Command: reflection-auto-ingest'
tags: []
---
# Reflection Auto-Ingest

Automatically processes reflection emails without manual invocation.

## Trigger
Email with `[Reflect]` in subject + audio attachment

## Behavior
1. Check Gmail every 5-15 minutes (configurable)
2. Find new emails matching pattern
3. Auto-download and stage
4. Auto-transcribe audio
5. Auto-run worker
6. Update registry to `awaiting-approval`
7. Optional: Send notification when complete

## Setup

### Enable Auto-Processing
```bash
python3 /home/workspace/N5/scripts/reflection_auto_ingest.py --enable --interval 10
```

This creates a scheduled task that runs every 10 minutes.

### Disable Auto-Processing
```bash
python3 /home/workspace/N5/scripts/reflection_auto_ingest.py --disable
```

### Check Status
```bash
python3 /home/workspace/N5/scripts/reflection_auto_ingest.py --status
```

## Configuration

Edit `file 'N5/config/reflection-sources.json'`:
```json
{
  "drive_folder_id": "YOUR_FOLDER_ID",
  "email_lookback_minutes": 10,
  "auto_process_email": true,
  "notify_on_complete": true
}
```

## Safety
- Only processes new messages (tracks message IDs)
- Never sends external emails automatically
- Only stages for approval, doesn't publish
- Logs all actions

## References
- file 'N5/scripts/reflection_auto_ingest.py'
- file 'N5/config/reflection-sources.json'
