---
description: "Command: auto-process-meetings"
tags:
tool: true
---
# Auto-Process Meetings Command

## What This Does

Checks the N5 inbox for pending meeting transcript requests and processes them using Zo's LLM capabilities (me!) to generate comprehensive meeting intelligence blocks.

## Workflow

1. **Check inbox**: `/home/workspace/N5/inbox/meeting_requests/`
2. **For each pending request**: 
   - Download/convert transcript if needed
   - Read full transcript content
   - Generate comprehensive intelligence blocks using my LLM
   - Save to `/home/workspace/N5/records/meetings/{meeting_id}/`
   - Mark request as completed
3. **Notify user** when processing is complete

## Usage

### Manual Trigger:

```markdown
User: "Process pending meeting requests"
OR
User: command 'N5/commands/auto-process-meetings.md'
```

### Automatic (Scheduled):

Set up a scheduled task that runs this command every 10-30 minutes.

## Processing Logic

For each transcript, I will:

1. **Read full transcript** (no token limits - I have full context)

2. **Extract intelligence blocks**:

   - MEETING_METADATA_SUMMARY
   - DETAILED_RECAP
   - RESONANCE_POINTS
   - SALIENT_QUESTIONS
   - DEBATE_TENSION_ANALYSIS
   - PRODUCT_IDEA_EXTRACTION
   - KEY_QUOTES_HIGHLIGHTS
   - DELIVERABLE_CONTENT_MAP
   - OUTSTANDING_QUESTIONS
   - STAKEHOLDER_MAP
   - And more...

3. **Generate comprehensive output** similar to the Carly meeting analysis

4. **Save to proper location** in N5 records

5. **Create notifications** for review

## Benefits Over External LLM APIs

✅ **Full context** - I can read entire transcript at once\
✅ **No API costs** - Uses Zo's built-in capabilities\
✅ **Customizable** - Can adapt to your preferences in real-time\
✅ **Interactive** - Can ask clarifying questions if needed\
✅ **Consistent quality** - Same LLM that processes all your other work\
✅ **Registry-driven** - Uses block_type_registry.json for dynamic templates

## Setup Instructions

### Step 1: Run Auto-Processor (Watcher)

```bash
# Run in background to detect new transcripts
nohup python3 /home/workspace/N5/scripts/meeting_auto_processor.py > /tmp/meeting_watcher.log 2>&1 &
```

### Step 2: Create Scheduled Task

```markdown
Schedule: Every 10 minutes
Command: "Check and process pending meeting requests at file 'N5/inbox/meeting_requests/'"
```

### Step 3: Test It

```markdown
1. Drop a meeting transcript in Document Inbox
2. Wait ~1 minute for detection
3. Check N5/inbox/meeting_requests/ for new request
4. Manually trigger: "Process pending meeting requests"
5. Verify output in N5/records/meetings/
```

## File Locations

- **Inbox**: `/home/workspace/N5/inbox/meeting_requests/` (pending requests)
- **Output**: `/home/workspace/N5/records/meetings/{meeting_id}/` (processed intelligence)
- **Logs**: `file N5/logs/processed_meetings.jsonl` (tracking)
- **Watch**: `/home/workspace/Document Inbox/` (new transcripts)

## Example Flow

```markdown
1. Fireflies uploads: "Carly x Careerspan-transcript-2025-09-23T21-04-28.138Z.docx"
   ↓
2. User downloads to Document Inbox (or auto-sync from Google Drive)
   ↓
3. meeting_auto_processor.py detects new file
   ↓
4. Creates request: N5/inbox/meeting_requests/carly-careerspan-2025-09-23_request.json
   ↓
5. Scheduled task triggers me: "Process pending meeting requests"
   ↓
6. I read transcript, generate intelligence blocks
   ↓
7. Save to: N5/records/meetings/carly-careerspan-2025-09-23/blocks.md
   ↓
8. User gets notification: "Meeting intelligence ready for Carly x Careerspan (2025-09-23)"
```

## Next Steps

1. Test the auto-processor script
2. Create scheduled task for automatic processing
3. Set up Google Drive sync (optional) for fully automatic workflow
4. Customize intelligence block templates as needed