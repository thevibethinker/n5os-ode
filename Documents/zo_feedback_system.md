# Zo Feedback System

**Version:** 1.0.0  
**Created:** 2025-10-30  
**Status:** ✅ Production

---

## Realtime Zo-Channel Feedback (Desktop)

In addition to the ZoReports pipeline below, there is a **direct Zo-channel feedback path** designed for fast reporting from Zo Desktop, especially during or right after agent runs.

**Components:**
- `file 'N5/scripts/zo_feedback.py'` – CLI for sending feedback directly to the Zo team
- `file 'Prompts/zo-feedback.prompt.md'` – N5 prompt wrapper (usable via `n5 zo-feedback`)
- **Slack (production)**: `#ext-zo-vrijen` (ID: `C09NDHKEXEJ`)
- **Slack (test)**: `#vrijen-slack-backend` (ID: `C085K7QE17C`) when `--test` is used
- **Drive folder**: `Zo Feedback` (ID: `1nNDtW4oXFablYY5hY9iTxEuK60cVwpLl`)

**Behavior:**
- BLUF (one-sentence summary) is posted to Slack
- Full context + attachments are written to `feedback.md` and media files inside a timestamped subfolder under **Zo Feedback** in Drive
- Messages **respect business hours** (9 AM – 6 PM ET, Mon–Fri): 
  - Outside that window, messages are scheduled for the next 9 AM
  - `--now` flag forces immediate send when truly urgent

**CLI Usage:**
```bash
# Simple praise (text-only, goes to #ext-zo-vrijen, scheduled if outside hours)
python3 N5/scripts/zo_feedback.py \
  -m "Image generation latency is fantastic" \
  -c praise

# Bug with context + screenshot
python3 N5/scripts/zo_feedback.py \
  -m "Zo Desktop error overlay masks screen" \
  -x "Error dialog flashes during long agent runs even when browser is closed." \
  -a /absolute/path/Xnip2025-11-26_02-25-04.jpg \
  -c bug \
  -p medium

# Test mode (non-Zo channel)
python3 N5/scripts/zo_feedback.py \
  -m "Testing feedback pipeline" \
  --test

# Urgent bug (send immediately, ignore scheduling)
python3 N5/scripts/zo_feedback.py \
  -m "Critical data-loss bug" \
  -c bug \
  -p high \
  --now
```

**N5 Command:**
```bash
n5 zo-feedback -m "BLUF summary" -x "Full context" -a /path/to/file.png -c bug -p high
```

The **ZoReports pipeline** below remains the structured, database-backed path for aggregated reporting and analytics. The **zo_feedback.py path** is optimized for:
- Fast, respectful notifications to the Zo team
- High-fidelity context capture during live usage
- Clean separation between test traffic (`#vrijen-slack-backend`) and production Zo channel (`#ext-zo-vrijen`).

---

## Overview

Lightweight feedback collection system for reporting issues, bugs, improvements, and questions to the Zo team. Captures context mid-conversation with optional attachments and automatically syncs to Google Drive.

**Key Features:**
- ✅ Zero-friction mid-conversation reporting
- ✅ Auto-captures conversation context (ID, tags, files, tools)
- ✅ Supports image/media attachments
- ✅ SQLite database for efficient querying
- ✅ Daily automated sync to Google Drive
- ✅ Persistent record (survives email bounces)

---

## Quick Start

### Submit Feedback

**CLI:**
```bash
python3 /home/workspace/N5/scripts/zo_report.py \
  --type bug \
  --severity high \
  --title "Session timeout" \
  --description "Script times out after 30s" \
  --attach /path/to/screenshot.png
```

**Natural Language (with Zo):**
```
"N5 report: the file browser has a glitch where files disappear 
after refresh, attaching screenshot"
```

### List Pending Reports
```bash
python3 /home/workspace/N5/scripts/zo_report.py --list-new
```

---

## Architecture

### Components

**1. Submission Script**  
`file 'N5/scripts/zo_report.py'`
- Captures feedback with optional attachments
- Auto-extracts conversation context
- Stores in SQLite database
- Copies attachments to managed directory

**2. Sync Orchestrator**  
`file 'N5/scripts/zo_feedback_orchestrator.py'`
- Queries new feedback from database
- Generates sync instructions (JSON)
- Marks items as sent after successful upload

**3. Recipe**  
`file 'Recipes/Zo Feedback Sync.md'`
- Handles actual Drive uploads (via Zo tools)
- Uploads attachments first, then reports
- Includes Drive links in report content

**4. Scheduled Task**  
Daily at 08:00 ET
- Automatically syncs pending feedback
- Uses `use_app_google_drive` tool
- Reports summary via email (if configured)

### Data Structure

**Database:** `file 'N5/data/zo_feedback.db'`

**Tables:**
- `feedback` - Main feedback records
- `feedback_attachments` - Attachment metadata

**Attachments:** `file 'N5/data/zo_feedback_attachments/{feedback_id}/'`

**Schema:** `file 'N5/schemas/zo_feedback.schema.json'`

---

## Feedback Types

| Type | Description | Examples |
|------|-------------|----------|
| **bug** | Something broken/not working | Crashes, errors, timeouts |
| **glitch** | Visual/UX issues | UI rendering, layout problems |
| **improvement** | Feature requests, enhancements | "Would love X feature" |
| **question** | Clarifications, how-to | "How do I...?", "Is this expected?" |

---

## Severity Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **high** | Blocks work, critical impact | Data loss, service down, security |
| **medium** | Impacts productivity | Annoying bugs, workarounds needed |
| **low** | Minor issues, nice-to-haves | Cosmetic issues, suggestions |

---

## Google Drive Integration

**Folder:** [ZoReports](https://drive.google.com/drive/folders/1FaNvdc3dJkRJe7aP7eRS8EWT9AGIsWrp)  
**Folder ID:** `1FaNvdc3dJkRJe7aP7eRS8EWT9AGIsWrp`

**Sharing:** Folder will be shared with Zo team for access

**Report Format:**
```
/ZoReports/
  feedback_high_severity.txt
  feedback_medium_severity.txt
  test_screenshot.png
  ...
```

Each report includes:
- Feedback ID (for tracking)
- Type and severity
- Description
- Conversation context
- Links to attachments (if any)

---

## Workflow

### User Flow
1. User encounters issue/has feedback
2. User runs CLI command or tells Zo: "N5 report: [description]"
3. System captures context + attachments
4. Feedback stored with status='new'
5. User confirmation: "✓ Will be sent in next daily sync"

### Sync Flow
1. Scheduled task triggers at 08:00 ET
2. Query database for status='new' items
3. For each item:
   - Upload attachments to Drive
   - Generate report with attachment links
   - Upload report to Drive
4. Mark all items as status='sent'
5. Report summary

---

## Context Capture

The system automatically captures:
- **Conversation ID** - Which conversation you were in
- **Session Tags** - From SESSION_STATE.md (if available)
- **Files Mentioned** - Files referenced in conversation (future)
- **Tools Used** - Zo tools used in conversation (future)

This helps the Zo team understand the context of your feedback.

---

## Testing

**Test Report Created:** 2025-10-30

**Test Cases:**
- ✅ Submit bug report (high severity, no attachment)
- ✅ Submit glitch report (medium severity, with attachment)
- ✅ List pending feedback
- ✅ Upload to Google Drive (both reports + attachment)
- ✅ Mark as sent in database
- ✅ Verify empty queue after sync

**Test Feedback IDs:**
- `zofb_20251030065815_c4e44d` - Bug report
- `zofb_20251030065822_96b2ef` - Glitch with attachment

---

## Usage Examples

### Example 1: Simple Bug Report
```bash
python3 /home/workspace/N5/scripts/zo_report.py \
  --type bug \
  --severity high \
  --title "API timeout" \
  --description "Google Drive API times out after 30 seconds on large files"
```

### Example 2: UI Glitch with Screenshot
```bash
python3 /home/workspace/N5/scripts/zo_report.py \
  --type glitch \
  --severity medium \
  --title "File browser refresh issue" \
  --description "Files disappear after refresh, must reload page" \
  --attach /home/workspace/Images/screenshot.png
```

### Example 3: Feature Request
```bash
python3 /home/workspace/N5/scripts/zo_report.py \
  --type improvement \
  --severity low \
  --title "Bulk file operations" \
  --description "Would love ability to select multiple files and move them at once"
```

### Example 4: Natural Language (via Zo)
```
Me: "N5 report: the scheduled task creation is confusing, 
     I keep forgetting the RRULE syntax. Can we add a helper?"

Zo: [Captures feedback automatically]
     ✓ Feedback submitted: zofb_20251030120000_abc123
     Will be sent in next daily sync (08:00 ET)
```

---

## Maintenance

### Check Pending Items
```bash
python3 /home/workspace/N5/scripts/zo_report.py --list-new
```

### Manual Sync (if needed)
Load file 'Recipes/Zo Feedback Sync.md' and tell Zo:
```
"Run the Zo Feedback Sync recipe"
```

### View Sync History
```bash
sqlite3 /home/workspace/N5/data/zo_feedback.db \
  "SELECT id, title, severity, status, sent_at FROM feedback ORDER BY sent_at DESC LIMIT 10"
```

### Database Queries
```sql
-- Count by severity
SELECT severity, COUNT(*) FROM feedback GROUP BY severity;

-- Recent high-severity items
SELECT * FROM feedback WHERE severity='high' ORDER BY timestamp DESC LIMIT 5;

-- Items with attachments
SELECT f.*, COUNT(a.id) as attachment_count 
FROM feedback f 
LEFT JOIN feedback_attachments a ON f.id = a.feedback_id 
GROUP BY f.id 
HAVING attachment_count > 0;
```

---

## Troubleshooting

### Issue: "Database not found"
**Solution:** Run a report first to initialize the database

### Issue: "Attachment not found"
**Solution:** Verify file path is absolute and file exists

### Issue: "Google Drive upload fails"
**Solution:** 
1. Check Drive connection in Zo settings
2. Verify folder ID is correct
3. Check Drive storage quota

### Issue: "Feedback not syncing"
**Solution:**
1. Check scheduled task is active: https://va.zo.computer/agents
2. View task logs for errors
3. Run manual sync to test

---

## Future Enhancements

**Potential additions:**
- [ ] Enhanced context capture (files mentioned, tools used)
- [ ] Support for video attachments
- [ ] Batch operations (mark multiple as resolved)
- [ ] Web UI for browsing feedback history
- [ ] Integration with Zo's internal issue tracker
- [ ] Auto-categorization via AI
- [ ] Sentiment analysis

---

## References

**Files:**
- `file 'N5/scripts/zo_report.py'` - Submission script
- `file 'N5/scripts/zo_feedback_orchestrator.py'` - Sync orchestrator
- `file 'N5/schemas/zo_feedback.schema.json'` - Data schema
- `file 'Recipes/Zo Feedback Sync.md'` - Sync recipe
- `file 'N5/data/zo_feedback.db'` - Database

**Drive:**
- [ZoReports Folder](https://drive.google.com/drive/folders/1FaNvdc3dJkRJe7aP7eRS8EWT9AGIsWrp)

**Scheduled Tasks:**
- View at: https://va.zo.computer/agents

---

*Last updated: 2025-10-30 03:00 ET*

