---
description: Process meeting transcripts automatically using Zo's LLM capabilities
  instead of external API calls.
tags: []
---
# Meeting Auto-Processor Command

## Purpose
Process meeting transcripts automatically using Zo's LLM capabilities instead of external API calls.

## Three Implementation Options

### Option 1: **Manual Trigger (Simplest - Works Now)**
```bash
# User provides Google Drive URL or file path
# Command: "Process this meeting transcript: [URL/file]"
# I download, convert, read, and generate intelligence blocks
# Works: ✅ (What we just did)
# Automatic: ❌
```

### Option 2: **File Watcher + Auto-Trigger (Recommended)**
```bash
# Watch Document Inbox for new .docx files from Fireflies
# When detected → automatically trigger me to process
# Works: ✅ (Can implement)
# Automatic: ✅
```

### Option 3: **Google Drive Integration + Scheduled Check (Advanced)**
```bash
# Monitor Google Drive folder for new Fireflies uploads
# Poll every hour or use webhooks
# Automatically download and process
# Works: ✅ (Requires setup)
# Automatic: ✅
```

## Implementation: Option 2 (File Watcher)

### Step 1: Create Watcher Service

Create: `file 'N5/scripts/meeting_watcher_service.py'`

```python
#!/usr/bin/env python3
"""
Meeting Transcript Auto-Processor
Watches Document Inbox for new transcript files and triggers Zo processing.
"""
import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

WATCH_DIR = "/home/workspace/Document Inbox"
TRIGGER_MARKER = "/tmp/meeting_transcript_ready"

class TranscriptHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Only process transcript files (Fireflies pattern)
        if "-transcript-" in filename.lower() and filename.endswith(('.docx', '.txt', '.pdf')):
            print(f"🎯 New transcript detected: {filename}")
            
            # Create trigger file for Zo to pick up
            with open(TRIGGER_MARKER, 'w') as f:
                f.write(filepath)
            
            print(f"✅ Trigger created: {TRIGGER_MARKER}")
            print(f"📢 Zo will process this automatically")

def main():
    print(f"👀 Watching for meeting transcripts in: {WATCH_DIR}")
    event_handler = TranscriptHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
```

### Step 2: Create Zo Processing Script

Create: `file 'N5/scripts/process_meeting_trigger.py'`

```python
#!/usr/bin/env python3
"""
Process meeting transcript when trigger file is detected.
This script is called BY Zo when a new transcript is ready.
"""
import sys
import os
from pathlib import Path
import json
import re

def extract_meeting_id(filename):
    """Extract meeting ID from Fireflies transcript filename."""
    # Pattern: "Name x Name-transcript-2025-09-23T21-04-28.138Z.docx"
    match = re.search(r'([^/]+)-transcript-(\d{4}-\d{2}-\d{2})', filename)
    if match:
        names = match.group(1).replace(' x ', '-').replace(' ', '-').lower()
        date = match.group(2)
        return f"{names}-{date}"
    return "unknown-meeting"

def main(transcript_path):
    meeting_id = extract_meeting_id(transcript_path)
    
    print(f"📋 Processing: {Path(transcript_path).name}")
    print(f"🆔 Meeting ID: {meeting_id}")
    
    # Create processing instruction file for Zo
    instruction_file = f"/tmp/zo_meeting_process_{meeting_id}.json"
    instruction = {
        "type": "meeting_intelligence",
        "transcript_path": transcript_path,
        "meeting_id": meeting_id,
        "requested_at": "auto",
        "output_dir": f"/home/workspace/N5/records/meetings/{meeting_id}"
    }
    
    with open(instruction_file, 'w') as f:
        json.dump(instruction, f, indent=2)
    
    print(f"✅ Instruction created: {instruction_file}")
    print(f"🤖 Zo should process this now")
    
    return instruction_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_meeting_trigger.py <transcript_path>")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    main(transcript_path)
```

### Step 3: Create Scheduled Task for Zo

```python
# Create scheduled task that checks for trigger files every 5 minutes
# When found: download from Drive if needed, process with my LLM, generate blocks
```

## Usage

### Manual (Current - Works Great):
```
User: "Process this meeting: https://docs.google.com/document/d/..."
Zo: Downloads → Converts → Reads full transcript → Generates intelligence blocks
```

### Automatic (With File Watcher):
```
1. Fireflies uploads transcript to Google Drive
2. User downloads to Document Inbox (or auto-sync)
3. File watcher detects new file
4. Creates trigger marker
5. Scheduled task picks up trigger
6. I (Zo) automatically process and generate blocks
7. User gets notification when complete
```

## Benefits

✅ **No external LLM APIs needed** - Uses Zo's built-in capabilities
✅ **Full context preserved** - I can see entire transcript, not limited by API chunking
✅ **Customizable output** - Can adapt blocks to your preferences in real-time
✅ **Error handling** - I can ask clarifying questions if transcript is ambiguous
✅ **Cost effective** - No per-token API costs

## Next Steps

1. **Install watchdog**: `pip install watchdog`
2. **Run watcher service**: As background process or registered service
3. **Create scheduled task**: Check trigger file every 5 minutes
4. **Set up Google Drive sync** (optional): Auto-download new Fireflies transcripts

## Alternative: Direct Command Registration

Register this as an N5 command:

```jsonl
{"command": "process-meeting", "description": "Process meeting transcript into intelligence blocks", "handler": "meeting_intelligence_orchestrator.py", "auto_trigger": "file_pattern:*-transcript-*.docx"}
```

Then it runs automatically when matching files appear.
