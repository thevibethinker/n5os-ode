---
description: Process pending AI requests from the meeting intelligence pipeline
tags: [meetings, automation, pipeline]
tool: true
---

# Process AI Request Queue

## Purpose
Process all pending AI requests in the meeting intelligence pipeline queue.

## Process

### 1. Find Pending Requests
```bash
ls -1 /home/workspace/N5/inbox/ai_requests/*.json
```

### 2. For Each Request File

**Load the request:**
```bash
cat /home/workspace/N5/inbox/ai_requests/[REQUEST_FILE].json
```

**Extract:**
- meeting_id
- transcript_path  
- prompt_name (should be "Meeting Process")

**Execute:**
Load file `Prompts/Meeting Process.md` and process the meeting according to its instructions.

**After processing, update the database:**
```bash
sqlite3 /home/workspace/N5/data/meeting_pipeline.db "UPDATE meetings SET status='complete', completed_at='$(date -u +%Y-%m-%dT%H:%M:%SZ)' WHERE meeting_id='[MEETING_ID]';"
```

**Create completion response:**
```bash
cat > /home/workspace/N5/inbox/ai_responses/[REQUEST_ID].json << 'EOF'
{
  "request_id": "[REQUEST_ID]",
  "status": "complete",
  "completed_at": "[TIMESTAMP]",
  "meeting_id": "[MEETING_ID]",
  "output_location": "/home/workspace/Personal/Meetings/[MEETING_ID]/"
}
EOF
```

**Move request to processed:**
```bash
mv /home/workspace/N5/inbox/ai_requests/[REQUEST_FILE].json /home/workspace/N5/inbox/ai_requests/processed/
```

### 3. Summary

Report:
- Total requests processed
- Meeting IDs completed
- Any errors encountered

## Notes

This is the CURRENT IMPLEMENTATION of AI request processing until the automated scheduled task is built.

The root issue was that `ai_request_processor.py` was a stub that queued requests but never executed them. This manual process closes that gap.
