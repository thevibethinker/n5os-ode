---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
---

# Old Meeting Processor Scripts - DEPRECATED

**Date**: 2025-11-15
**Reason**: Replaced by prompt-based meeting processing system

## Archived Scripts

1. **process_meeting_transcript.py** - OLD delegation script
   - Created processing requests for Zo to handle
   - **Replaced by**: `Prompts/drive_meeting_ingestion.prompt.md` + `Prompts/Meeting Process.prompt.md`

2. **run_meeting_processor.py** - OLD API integration runner
   - Required Google Calendar/Gmail API access
   - **Replaced by**: Direct prompt-based processing

## Current System (2025-11-15)

**Pipeline:**
1. Fireflies → Google Drive (automated)
2. `drive_meeting_ingestion.prompt.md` - Downloads transcripts, converts to markdown
3. Transcripts land in `Personal/Meetings/Inbox/`
4. `Process AI Request Queue.prompt.md` - Processes pending requests
5. `Meeting Process.prompt.md` - Generates intelligence blocks using B##_UPPERCASE format

**File Naming Convention**: `B##_BLOCKNAME.md` (e.g., `B08_STAKEHOLDER_INTELLIGENCE.md`)

## Why Deprecated

- Old scripts delegated to "future Zo" instead of processing directly
- Created request files that required manual intervention
- Prompt-based system is simpler, more maintainable, and directly executable
