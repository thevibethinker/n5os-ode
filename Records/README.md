# Records/

**Purpose**: Staging area for raw, unprocessed data before ingestion into Knowledge or Lists.

---

## Overview

Records/ is the **intake point** for all unprocessed information:
- Meeting transcripts awaiting processing
- Emails needing review or ingestion
- Documents requiring analysis
- Notes pending organization

**Key Principle**: Records/ is temporary storage. Files should be **processed then archived or deleted**.

---

## Directory Structure

```
Records/
├── Company/
│   ├── meetings/       - Meeting transcripts (pre-processing)
│   ├── emails/         - Important company emails
│   ├── documents/      - Company docs needing ingestion
│   └── inbox/          - General company intake queue
├── Personal/
│   ├── notes/          - Personal notes
│   ├── drafts/         - Ad hoc generated outputs (emails, documents)
│   │   ├── emails/     - Email drafts
│   │   ├── documents/  - Document drafts
│   │   └── other/      - Miscellaneous generated content
│   └── inbox/          - Personal intake queue
├── Temporary/          - Short-term processing queue (7-day auto-cleanup)
└── README.md           - This file
```

---

## Processing Flow

### 1. Intake
Files arrive in Records/ via:
- Manual placement (drag & drop)
- Email forwarding
- Automation (save_webpage, transcriptions, etc.)
- Download commands

### 2. Review
Periodic review of Records/:
- Check Records/*/inbox/ daily
- Identify files needing processing
- Prioritize by importance/urgency

### 3. Process
Use N5 commands to extract information:
```bash
# Process meeting transcript
N5: process-record Records/Company/meetings/2025-10-08-board-meeting.md

# This extracts:
# - Facts → Knowledge/facts.jsonl
# - Company info → Knowledge/company.md

# Ad hoc generated drafts
# - Created → Records/Personal/drafts/[type]/
# - Review/edit in place
# - Send/publish
# - Archive or delete after action taken
```

### 4. Archive or Delete
After processing:
- **Archive**: Move to external storage if needed for reference
- **Delete**: Remove if fully ingested and no longer needed

---

## Retention Policy

### Company/
- **meetings/**: Process within 48 hours, archive externally after 30 days
- **emails/**: Process within 24 hours, delete after processing
- **documents/**: Process within 7 days, archive externally after 14 days
- **inbox/**: Process within 24 hours

### Personal/
- **notes/**: Process within 7 days
- **inbox/**: Process within 48 hours

### Temporary/
- **Auto-cleanup**: Files older than 7 days are automatically deleted
- Use for: Short-term downloads, intermediate processing files

---

## File Naming Conventions

Use descriptive, date-prefixed names:
```
Good:
- 2025-10-08-board-meeting-transcript.md
- 2025-10-08-investor-email-sequoia.md
- 2025-10-08-gtm-strategy-doc.pdf

Bad:
- transcript.md (too generic)
- meeting.md (no date or context)
- document.pdf (no description)
```

---

## Commands for Processing

### Available Commands
- `process-record` - General record processing
- `transcript-ingest` - Process meeting transcripts
- `direct-knowledge-ingest` - Process documents with LLM
- `knowledge-ingest` - Batch process multiple files

### Usage Examples
```
# Process a single meeting transcript
N5: process-record Records/Company/meetings/2025-10-08-board-meeting.md

# Process entire inbox
N5: process-inbox Records/Company/inbox/

# Process with custom routing
N5: process-record Records/Company/documents/strategy.pdf --extract-facts --create-tasks
```

---

## Integration with N5 Workflows

### Email → Records → Knowledge
```
1. Forward email to va@zo.computer
2. Email saved to Records/Company/emails/
3. Daily automation processes inbox
4. Facts extracted to Knowledge/
5. Action items added to Lists/
6. Email archived or deleted
```

### Meeting → Records → Knowledge
```
1. Upload transcript to Records/Company/meetings/
2. Run: N5: process-record [file]
3. Transcript analyzed by LLM
4. Key points → Knowledge/company.md
5. Action items → Lists/must-contact.jsonl
6. Decisions → Knowledge/facts.jsonl
7. Transcript archived externally
```

### Document → Records → Knowledge
```
1. Save document to Records/Company/documents/
2. Run: direct-knowledge-ingest [file]
3. Document processed with full context
4. Information distributed to appropriate files
5. Document archived or deleted
```

---

## Best Practices

### DO:
✅ Use Records/ for all new unprocessed files
✅ Process files within retention window
✅ Delete or archive after processing
✅ Use descriptive file names with dates
✅ Check inbox folders daily

### DON'T:
❌ Let files accumulate unprocessed
❌ Use Records/ for permanent storage
❌ Save processed information here
❌ Use generic file names
❌ Store large files long-term (use external archive)

---

## Monitoring

### Health Check
Run periodically:
```bash
# Check for old files
find Records/ -type f -mtime +7

# Count unprocessed files
find Records/*/inbox/ -type f | wc -l

# Review Temporary/ for cleanup
ls -lh Records/Temporary/
```

### Alerts
Set up alerts for:
- Files older than retention policy
- Large files (>10MB) in Records/
- High count of unprocessed items (>20)

---

## Related Documentation

- file 'Knowledge/README.md' - Where processed information lives
- file 'Lists/README.md' - Where action items are tracked
- file 'N5/prefs/prefs.md' - File saving policy
- file 'Documents/N5.md' - System entry point

---

*Records/ is the gateway to N5 OS - everything starts here before becoming structured knowledge.*
