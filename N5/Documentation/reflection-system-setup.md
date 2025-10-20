# Reflection System Setup & Testing Guide

**Version:** 1.0  
**Date:** 2025-10-20  
**Status:** Ready for testing

---

## Overview

Complete reflection ingestion pipeline supporting:
- **Email source**: `[Reflect]` subject tag with audio attachments
- **Drive source**: Regular folder sync for text/audio reflections
- **Manual invocation**: No scheduled automation
- **Approval workflow**: All reflections staged for review before output generation

---

## Architecture

```
Sources → Staging → Transcription → Processing → Approval → Outputs
  ↓          ↓           ↓              ↓           ↓          ↓
Email    incoming/   .transcript    worker.py   registry   outputs/
Drive                  .jsonl                   (awaiting)
```

### Key Components

1. **`reflection-ingest`** - Unified command (email + Drive)
2. **`reflection_worker.py`** - Processes individual files
3. **`reflection_pipeline.py`** - Legacy Drive-only script
4. **State tracking** - Deduplication via `.state.json`
5. **Registry** - Approval workflow tracking

---

## Setup Instructions

### 1. Configure Drive Folder ID

Edit `file 'N5/config/reflection-sources.json'`:

```json
{
  "drive_folder_id": "YOUR_ACTUAL_FOLDER_ID_HERE",
  "email_lookback_minutes": 10
}
```

**To find your folder ID:**
- Open folder in Drive
- URL format: `https://drive.google.com/drive/folders/[FOLDER_ID]`
- Copy the ID after `/folders/`

### 2. Test Email Ingestion

1. **Send test email** to your Zo email address:
   - Subject: `[Reflect] Test reflection on product strategy`
   - Body: "Focus on positioning vs competitors. Be concise."
   - Attachment: Any audio file (mp3, m4a, wav, opus)

2. **Run ingestion**:
   ```bash
   command 'N5/commands/reflection-ingest.md' --source email
   ```

3. **Expected results**:
   - Audio downloaded to `N5/records/reflections/incoming/`
   - Body text saved as `<filename>_context.md`
   - Message ID tracked in `.state.json`

### 3. Test Drive Ingestion

1. **Upload file** to configured Drive folder:
   - Text reflection (md, txt, docx)
   - OR audio file (mp3, m4a, etc.)

2. **Run ingestion**:
   ```bash
   command 'N5/commands/reflection-ingest.md' --source drive
   ```

3. **Expected results**:
   - File downloaded to `incoming/`
   - File ID tracked in `.state.json`

### 4. Test Audio Transcription

**Important**: The worker expects transcripts to exist. Zo must transcribe audio before processing.

**Manual transcription**:
```bash
# Via Zo's tool
transcribe_audio('/home/workspace/N5/records/reflections/incoming/audio.m4a')
```

**Automatic transcription** (when calling from Zo):
```bash
# Zo handles this automatically when you invoke the command
command 'N5/commands/reflection-ingest.md'
```

### 5. Verify Worker Processing

Check outputs:
```bash
ls -la N5/records/reflections/outputs/
ls -la N5/records/reflections/registry/
```

Expected structure:
```
outputs/
└── {YYYY-MM-DD}/
    └── {slug}/
        ├── summary.md
        └── detail.md

registry/
└── registry.json  # Status: awaiting-approval
```

---

## Email Body + Audio Pattern

When email contains both body text and audio:

- **Body** = Instructions/context
  - Example: "Make this punchy for LinkedIn. Focus on the 'aha moment'."
  
- **Audio** = Actual reflection content
  - Transcribed and processed as primary content
  
- **Worker behavior**:
  - Loads `<filename>_context.md` automatically
  - Includes context in summary header
  - Uses instructions to guide classification/voice selection

---

## Usage Patterns

### Daily Drive Sync
```bash
# Pull latest from Drive, process all new files
command 'N5/commands/reflection-ingest.md' --source drive
```

### Email on the Go
1. Record voice memo
2. Email to Zo with `[Reflect]` subject
3. Run: `command 'N5/commands/reflection-ingest.md' --source email`

### Bulk Processing
```bash
# Check both sources, process everything new
command 'N5/commands/reflection-ingest.md'
```

### Manual File Drop
1. Copy files directly to `N5/records/reflections/incoming/`
2. Run: `command 'N5/commands/reflection-ingest.md'`
3. Script auto-detects manually staged files

---

## Approval Workflow

### 1. Review Pending Reflections
```bash
cat N5/records/reflections/registry/registry.json | jq '.items[] | select(.status=="awaiting-approval")'
```

### 2. Check Proposal
```bash
cat Records/Reflections/Proposals/{slug}_proposal.md
```

### 3. Approve & Generate Outputs
*(Future enhancement - manual for now)*

1. Select desired outputs (LinkedIn, memo, blog, etc.)
2. Trigger output generation
3. Status updates to `approved` → `generated`

---

## Troubleshooting

### Audio not transcribing
**Issue**: Worker fails with "Missing transcript"  
**Fix**: Ensure Zo's `transcribe_audio` tool runs first
```bash
# Manual transcription
transcribe_audio('<path-to-audio>')

# Then rerun worker
python3 N5/scripts/reflection_worker.py --file <path-to-audio>
```

### Email not found
**Issue**: `gmail-find-email` returns no results  
**Check**:
- Email sent within last 10 minutes?
- Subject contains `[Reflect]`?
- Has audio attachment?
- File extension: mp3, m4a, wav, opus?

### Drive files not pulling
**Issue**: Drive ingestion returns empty  
**Fix**:
1. Verify `drive_folder_id` in config
2. Check Zo has Drive permissions
3. Confirm files are in correct folder

### Duplicate processing
**Issue**: Same reflection processed twice  
**Check**: `.state.json` tracking
- `processed_message_ids` for email
- `processed_file_ids` for Drive

---

## State Files Reference

### `.state.json`
```json
{
  "last_run_iso": "2025-10-20T05:30:00",
  "processed_file_ids": ["drive-file-id-1", "drive-file-id-2"],
  "processed_message_ids": ["email-msg-id-1"]
}
```

### `registry.json`
```json
{
  "items": [
    {
      "id": "2025-10-20_monetizing-zo",
      "source": "/path/to/audio.m4a",
      "ingested_at": "2025-10-20T05:30:00",
      "status": "awaiting-approval",
      "outputs": {
        "summary": "/path/to/summary.md",
        "detail": "/path/to/detail.md",
        "proposal": "/path/to/proposal.md"
      }
    }
  ]
}
```

---

## Next Steps

1. **Test email ingestion** - Send test `[Reflect]` email
2. **Configure Drive folder** - Add actual folder ID
3. **Run full flow** - Email → Ingest → Transcribe → Process → Review
4. **Refine classification** - Adjust heuristics based on real reflections
5. **Build approval UI** - Interactive selection of output formats
6. **Add output generation** - LinkedIn, memo, blog templates

---

## Related Files

- command 'N5/commands/reflection-ingest.md'
- command 'N5/commands/reflection-pipeline.md'
- command 'N5/commands/reflection-email-orchestrator.md'
- command 'N5/commands/reflection-worker.md'
- file 'N5/scripts/reflection_ingest.py'
- file 'N5/scripts/reflection_worker.py'
- file 'N5/config/reflection-sources.json'
- file 'N5/records/reflections/.state.json'

---

**Ready for Production**: ✅ (with manual transcription)  
**Ready for Full Automation**: ⏳ (pending Zo tool integration)
