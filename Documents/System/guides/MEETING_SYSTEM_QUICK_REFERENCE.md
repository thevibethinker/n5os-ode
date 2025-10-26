# Meeting Processing System — Quick Reference

**Version:** 3.0  
**Status:** Production Active  
**Quick access guide for common tasks**

---

## Table of Contents

1. [Common Commands](#common-commands)
2. [How to Process Meetings](#how-to-process-meetings)
3. [Monitoring & Verification](#monitoring--verification)
4. [Meeting Types & Stakeholders](#meeting-types--stakeholders)
5. [Processing Modes](#processing-modes)
6. [Complete Workflow](#complete-workflow)
7. [Testing the System](#testing-the-system)
8. [Output Files Guide](#output-files-guide)
9. [Troubleshooting](#troubleshooting)
10. [Customization](#customization)
11. [Example Workflows](#example-workflows)
12. [File Locations Reference](#file-locations-reference)

---

## Common Commands

### Process a Single Meeting

```bash
# From local file
N5: meeting-process /path/to/transcript.txt \\
  --type sales \\
  --stakeholder customer_founder

# From Google Drive
N5: meeting-process <gdrive_file_id> \\
  --type coaching \\
  --stakeholder candidate_job_seeker

# Quick mode (action items only)
N5: meeting-process transcript.txt \\
  --type networking \\
  --stakeholder community_manager \\
  --mode quick

# With simulation mode (testing)
python3 /home/workspace/N5/scripts/meeting_intelligence_orchestrator.py \\
  --transcript_path \"test.txt\" \\
  --meeting_id \"test-001\" \\
  --use-simulation

# Auto-create Gmail draft
N5: meeting-process transcript.txt \\
  --type sales \\
  --stakeholder customer_founder \\
  --output-format gmail-draft
```

### Batch Process from Google Drive Folder

```bash
N5: transcript-ingest <gdrive_folder_id> \\
  --auto-classify \\
  --batch-size 5
```

### Process Pending Meeting Requests

```bash
# Via user command
\"Process pending meeting requests\"

# Via command reference
command 'N5/commands/auto-process-meetings.md'
```

---

## How to Process Meetings

### Option 1: Manual Processing (Recommended for testing)

Just say to Zo:
```
\"Process the pending meeting request\"
```

Zo will:
1. Read the request JSON
2. Load the full transcript
3. Generate comprehensive intelligence blocks
4. Save to `N5/records/meetings/{meeting-id}/blocks.md`

### Option 2: Using the Command

```
command 'N5/commands/auto-process-meetings.md'
```

### Option 3: Semi-Automatic Workflow

```
1. New transcript arrives in Document Inbox
   ↓
2. Run: python3 N5/scripts/meeting_auto_processor.py --once
   (or keep running in background)
   ↓
3. Processing request created in N5/inbox/meeting_requests/
   ↓
4. You say: \"Process pending meeting requests\"
   ↓
5. Zo reads transcript + generates intelligence blocks
   ↓
6. Output saved to N5/records/meetings/{id}/blocks.md
```

### Option 4: Fully Automatic Workflow

```
1. New transcript arrives in Document Inbox
   ↓
2. Background service detects it immediately
   ↓
3. Scheduled task triggers Zo every 10 minutes
   ↓
4. Zo automatically processes and generates blocks
   ↓
5. You get notification: \"Meeting intelligence ready!\"
```

**Setup for Fully Automatic:**
1. Register detector as background service:
   ```bash
   nohup python3 /home/workspace/N5/scripts/meeting_auto_processor.py > /tmp/meeting_watcher.log 2>&1 &
   ```

2. Create scheduled task:
   - Frequency: Every 10 minutes
   - Instruction: \"Check for pending meeting requests in N5/inbox/meeting_requests/ and process them\"

---

## Monitoring & Verification

### Check System Status

**Via Zo Scheduler:**  
Visit: https://va.zo.computer/schedule

Look for:
- Task name: Meeting processing task
- Frequency: Every 10 minutes (or your configured interval)
- Next run: [upcoming time]
- Status: Active

### Monitor Processing Log

```bash
# View entire log
cat N5/logs/processed_meetings.jsonl | jq .

# Watch for changes (leave running)
watch -n 60 'tail -3 N5/logs/processed_meetings.jsonl'

# Count processed transcripts
wc -l N5/logs/processed_meetings.jsonl

# Show most recent processing
tail -5 N5/logs/processed_meetings.jsonl | jq .

# What was processed in last 24 hours?
cat N5/logs/processed_meetings.jsonl | \\
  jq 'select(.processed_at > (now - 86400 | todate))'
```

### Check for New Meeting Outputs

```bash
# List recent meetings
ls -lt /home/workspace/N5/records/meetings/ | head -10

# Count total processed meetings
ls -1 /home/workspace/N5/records/meetings/ | wc -l

# View specific meeting output
cat /home/workspace/N5/records/meetings/{meeting-id}/blocks.md

# Check extraction requests
ls -la /home/workspace/N5/records/meetings/{meeting-id}/extraction_requests/
```

### Check Pending Requests

```bash
# List pending meeting requests
ls -1 /home/workspace/N5/inbox/meeting_requests/

# View specific request
cat /home/workspace/N5/inbox/meeting_requests/{meeting-id}_request.json | jq .
```

### Verify Auto-Detector is Running

```bash
# Check if process is running
ps aux | grep meeting_auto_processor

# View detector logs
tail -f /tmp/meeting_watcher.log

# Run detector once (test mode)
python3 /home/workspace/N5/scripts/meeting_auto_processor.py --once
```

---

## Meeting Types & Stakeholders

### Meeting Types

| Type | Use When | Key Blocks Generated |
|------|----------|----------------------|
| `sales` | Customer/prospect meetings | Deal intelligence, buying signals |
| `community_partnerships` | Partnership discussions | Partnership scope, collaboration terms |
| `coaching` | Career coaching sessions | Career insights, development plans |
| `networking` | Networking conversations | Warm intros, connection opportunities |
| `fundraising` | Investor meetings | Investor thesis, due diligence |

**Multi-classification:** Use comma-separated types
```bash
--type sales,community_partnerships
```

### Stakeholder Types

| Type | Description |
|------|-------------|
| `customer_founder` | Company founder/CEO customer |
| `customer_hiring_manager` | Hiring manager customer |
| `customer_recruiting_lead` | Recruiting lead customer |
| `customer_channel_partner` | Channel/referral partner |
| `community_manager` | Community leader/organizer |
| `candidate_job_seeker` | Job seeker you're coaching |
| `investor` | Angel investor |
| `vc` | Venture capital investor |

**Multi-stakeholder:** Use comma-separated types
```bash
--stakeholder vc,customer_channel_partner
```

---

## Processing Modes

| Mode | Blocks | Duration | Best For |
|------|--------|----------|----------|
| `quick` | Action items only | ~30s | Quick extraction |
| `essential` | Follow-up email, action items, decisions | ~1-2 min | Standard workflow |
| `full` | All applicable blocks | ~3-5 min | Complete analysis |

**Default:** `full`

---

## Complete Workflow

### Current Setup (Semi-Automatic)

**What Just Happened:**
1. **Detection**: Auto-processor scanned `Document Inbox/`
2. **Found**: New transcript file
3. **Created request**: `N5/inbox/meeting_requests/{meeting-id}_request.json`
4. **Logged**: Added to `N5/logs/processed_meetings.jsonl`

**To Process:**
- Say: \"Process pending meeting requests\"
- Or run detector: `python3 N5/scripts/meeting_auto_processor.py --once`

### Future Setup (Fully Automatic)

1. **Detection layer** runs continuously in background
2. **Queue layer** stores pending requests
3. **Processor layer** (Zo) triggered by scheduled task
4. **Notification** when complete

**Why This Works Better:**

**Old Way (external APIs):**
- ❌ Tries to call external LLM APIs
- ❌ APIs not configured → fails
- ❌ Falls back to placeholder/simulation data
- ❌ Result: Wrong names, generic content

**New Way (Zo-integrated):**
- ✅ Uses Zo's built-in LLM capabilities
- ✅ Full transcript context always available
- ✅ No external dependencies or API keys
- ✅ Result: High-quality, accurate intelligence blocks

---

## Testing the System

### Option 1: Wait for Next Scheduled Run
The system will automatically check at configured interval (e.g., every 10 minutes).

### Option 2: Upload Test Transcript
1. Add a new transcript to `Document Inbox/`
2. Run detector: `python3 N5/scripts/meeting_auto_processor.py --once`
3. Process: \"Process pending meeting requests\"
4. Check output in `N5/records/meetings/`

### Option 3: Trigger Manually
Just tell Zo:
```
Process any new meeting transcripts now
```

### Option 4: Use Simulation Mode
Test without real LLM calls:
```bash
python3 /home/workspace/N5/scripts/meeting_intelligence_orchestrator.py \\
  --transcript_path \"test_transcript.txt\" \\
  --meeting_id \"test-sim\" \\
  --use-simulation
```

---

## Output Files Guide

### What Gets Created

For each processed transcript:

```
/home/workspace/N5/records/meetings/{meeting-id}/
├── blocks.md                      # All intelligence blocks (v3.0)
├── extraction_requests/           # LLM request/response files
│   ├── request_{timestamp}.json
│   └── response_{timestamp}.json
│
└── (v2.0 structure also supported)
    ├── REVIEW_FIRST.md           # Executive dashboard
    ├── transcript.txt            # Original transcript
    ├── _metadata.json            # Structured metadata
    │
    ├── OUTPUTS/                  # Ready-to-use outputs
    │   ├── follow_up_email.md
    │   └── warm_intro_*.md
    │
    └── INTELLIGENCE/             # Analysis & insights
        ├── action_items.md
        ├── decisions.md
        ├── key_insights.md
        └── stakeholder_profile.md
```

### What to Review First (v2.0 format)

1. **`REVIEW_FIRST.md`** - Executive dashboard
   - Priority actions
   - Key metrics
   - Quick links to all blocks

### Ready-to-Use Outputs

2. **`OUTPUTS/follow_up_email.md`** - Copy/paste into email
3. **`OUTPUTS/warm_intro_*.md`** - One file per intro

### Intelligence Files

4. **`INTELLIGENCE/action_items.md`** - Your tasks + their tasks
5. **`INTELLIGENCE/decisions.md`** - Decisions made
6. **`INTELLIGENCE/key_insights.md`** - Strategic takeaways
7. **`INTELLIGENCE/stakeholder_profile.md`** - CRM enrichment

### Optional Intelligence (if detected)

8. **`INTELLIGENCE/risks.md`** - Concerns, blockers
9. **`INTELLIGENCE/opportunities.md`** - Upsells, partnerships
10. **`INTELLIGENCE/user_research.md`** - Pain points, quotes
11. **`INTELLIGENCE/competitive_intel.md`** - Competitors mentioned

### Category-Specific

12. **`INTELLIGENCE/deal_intelligence.md`** (sales)
13. **`INTELLIGENCE/career_insights.md`** (coaching/networking)
14. **`INTELLIGENCE/investor_thesis.md`** (fundraising)
15. **`INTELLIGENCE/partnership_scope.md`** (community_partnerships)

### Block Generation Logic

**Universal Blocks** (always generated):
- Follow-up email
- Action items
- Decisions
- Key insights
- Stakeholder profile

**Conditional Blocks** (generated if content detected, 70%+ confidence):
- Warm intros
- Risks
- Opportunities
- User research (80%+ confidence)
- Competitive intel (80%+ confidence)

**Category-Specific Blocks** (based on meeting type):
- Deal intelligence → `--type sales`
- Career insights → `--type coaching` or `networking`
- Investor thesis → `--type fundraising`
- Partnership scope → `--type community_partnerships`

---

## Troubleshooting

### Detection Issues

**\"No new transcripts detected\"**
- Check file is in `/home/workspace/Document Inbox/`
- Verify filename matches patterns (`*-transcript-*`)
- Check permissions: `ls -la \"/home/workspace/Document Inbox/\"`
- Review processed log to avoid duplicates

**\"Processing request created but not processed\"**
- Manually trigger: \"Process pending meeting requests\"
- Check scheduled task is running (https://va.zo.computer/schedule)
- Verify request JSON is valid: `cat N5/inbox/meeting_requests/*.json`

### Processing Issues

**\"Transcript File Not Found\"**
**Error:** `FileNotFoundError: Transcript not found`  
**Solution:** 
- Check path is correct
- Use absolute path
- Ensure file exists

**\"Configuration File Missing\"**
**Error:** `FileNotFoundError: content-library.json not found`  
**Solution:**
- Check default paths exist:
  - `/home/workspace/N5/prefs/communication/content-library.json`
  - `/home/workspace/N5/prefs/block_type_registry.json`
- Use `--essential_links_path` and `--block_registry_path` arguments

**\"No Blocks Generated\"**
- Check log file: `cat /home/workspace/N5/logs/orchestrator_{meeting_id}.log`
- Verify extraction requests created: `ls extraction_requests/`
- Try simulation mode: `--use-simulation`
- Validate registry JSON: `jq . /home/workspace/N5/prefs/block_type_registry.json`

**\"Output quality not good enough\"**
- Provide specific feedback on what to improve
- Zo learns and adapts to your preferences
- Ensure full transcript is being read
- Check transcript format (clean text vs. complex formatting)

### Integration Issues

**\"No Email History\"**
**Message:** \"Email history: not found\"  
**Note:** Non-critical, processing continues. Check Gmail app connection if needed.

**\"Google Drive Error\"**
**Error:** `Google Drive fetch failed`  
**Solution:** 
- Verify app connection
- Check file permissions
- Ensure valid file ID

**\"Low Confidence Blocks Skipped\"**
**Message:** Block skipped (confidence < 70%)  
**Explanation:** System detected content but confidence too low. Review transcript manually if needed.

### Service Issues

**\"Background detector not running\"**
```bash
# Check if process is running
ps aux | grep meeting_auto_processor

# Restart if needed
cd /home/workspace/N5/scripts
nohup python3 meeting_auto_processor.py > /tmp/meeting_watcher.log 2>&1 &
```

**\"Processing log corrupted\"**
```bash
# Backup and recreate
cp N5/logs/processed_meetings.jsonl N5/logs/processed_meetings.jsonl.backup
# Manually recreate or clear
```

---

## Customization

### Adjust Intelligence Blocks

Edit: `file 'N5/prefs/block_type_registry.json'`

Add/remove/modify blocks:
- Add new block types
- Change formatting
- Adjust what gets extracted

### Adjust Processing Frequency

**Detector interval:**
Edit `CHECK_INTERVAL` in `meeting_auto_processor.py`:
```python
CHECK_INTERVAL = 60  # seconds (current: 1 minute)
```

**Scheduled task:**
- Adjust at https://va.zo.computer/schedule
- Common frequencies:
  - Every 10 minutes: `FREQ=MINUTELY;INTERVAL=10`
  - Every hour: `FREQ=HOURLY;INTERVAL=1`
  - Every 30 minutes: `FREQ=HOURLY;INTERVAL=1;BYMINUTE=0,30`

### Adjust Triggers

Edit patterns in `meeting_auto_processor.py`:
```python
transcript_patterns = [
    \"*-transcript-*.docx\",  # Fireflies pattern
    \"*-transcript-*.txt\",
    \"*meeting-notes*.docx\",  # Add custom patterns
]
```

### Change Output Format

**Transcript Format Requirements:**
- Plain text (.txt)
- Markdown (.md)
- Word documents (.docx) - requires pandoc

**Recommended structure:**
```
[Speaker Name]: [Content]
[Speaker Name]: [Content]
```

**Example:**
```
Vrijen Attawar: Thanks for joining today.
Logan Currie: Happy to be here!
```

---

## Example Workflows

### Workflow 1: Standard Sales Call

```bash
# 1. Process meeting
N5: meeting-process transcript.txt \\
  --type sales \\
  --stakeholder customer_founder \\
  --mode essential

# 2. Review output
cat REVIEW_FIRST.md  # or blocks.md for v3.0

# 3. Send follow-up
# (Copy from OUTPUTS/follow_up_email.md)

# 4. Check action items added
N5: lists-find action-items --recent 5
```

### Workflow 2: Quick Networking Call

```bash
# Fast extraction
N5: meeting-process transcript.txt \\
  --type networking \\
  --stakeholder candidate_job_seeker \\
  --mode quick

# Review action items only
cat INTELLIGENCE/action_items.md
```

### Workflow 3: Important Partnership Discussion

```bash
# Full analysis
N5: meeting-process transcript.txt \\
  --type community_partnerships,sales \\
  --stakeholder customer_channel_partner \\
  --mode full

# Review everything
cat REVIEW_FIRST.md  # or blocks.md

# Check for warm intros
ls OUTPUTS/warm_intro_*

# Review partnership scope
cat INTELLIGENCE/partnership_scope.md
```

### Workflow 4: Automated Processing

```bash
# 1. Drop transcript in Document Inbox
cp new_transcript.txt \"/home/workspace/Document Inbox/\"

# 2. Wait for detection (or run manually)
python3 /home/workspace/N5/scripts/meeting_auto_processor.py --once

# 3. Process (automatically or manually)
# Automatic: Wait for scheduled task
# Manual: \"Process pending meeting requests\"

# 4. Review output
ls -lt /home/workspace/N5/records/meetings/ | head -1
```

---

## File Locations Reference

### Commands
- Main command: `file 'N5/commands/meeting-process.md'`
- Batch ingest: `file 'N5/commands/transcript-ingest.md'`
- Auto-process: `file 'N5/commands/auto-process-meetings.md'`
- Follow-up generator: `file 'N5/commands/follow-up-email-generator.md'`

### Scripts
- **Orchestrator:** `file 'N5/scripts/meeting_intelligence_orchestrator.py'`
- **Auto-detector:** `file 'N5/scripts/meeting_auto_processor.py'`
- **Blocks:** `file 'N5/scripts/blocks/'` (v2.0 modules)

### Configuration
- **Block Registry:** `file 'N5/prefs/block_type_registry.json'`
- **Essential Links:** `file 'N5/prefs/communication/content-library.json'`

### Schemas
- **Metadata:** `file 'N5/schemas/meeting-metadata.schema.json'`
- **Index:** `file 'N5/schemas/index.schema.json'`
- **Lists:** `file 'N5/schemas/lists.item.schema.json'`

### Outputs
- **Meetings directory:** `/home/workspace/N5/records/meetings/`
- **Request queue:** `/home/workspace/N5/inbox/meeting_requests/`
- **Lists integration:** `file 'N5/lists/'`
- **Logs:** `/home/workspace/N5/logs/`

---

## Integration with N5 Lists

### Automatic List Population

**Action Items:**
```bash
# View your action items from meeting
N5: lists-find action-items --filter \"meeting_id=a83f92\"
```

**Warm Intros:**
```bash
# View pending intros
N5: lists-find warm-intros --status pending
```

**Must Contact:**
```bash
# High-priority follow-ups
N5: lists-find must-contact --urgency high
```

### Manual List Operations

**Add item to list:**
```bash
N5: lists-add action-items \"Follow up with Logan about pricing\"
```

**Update item:**
```bash
N5: lists-set action-items <item_id> --status completed
```

---

## Tips & Best Practices

### For Best Results

1. **Include meeting context in filename:** `2025-10-09_sales_call_acme_corp.txt`
2. **Use consistent speaker labeling:** `Logan:` vs `LC:` (pick one format)
3. **Include timestamps if available:** Improves duration estimation
4. **Add meeting date in transcript header:** Improves metadata extraction
5. **Keep transcripts organized:** Name them clearly for better meeting ID extraction
6. **Run detector once after manual downloads:** `--once` flag is quick
7. **Set up Google Drive sync:** Auto-download Fireflies transcripts to Document Inbox
8. **Review first few outputs:** Provide feedback so Zo can refine extraction style

### Workflow Recommendations

**Post-Meeting Checklist:**
1. Run `meeting-process` with appropriate flags
2. Review `REVIEW_FIRST.md` (v2.0) or `blocks.md` (v3.0)
3. Edit `OUTPUTS/follow_up_email.md` if needed
4. Send follow-up email
5. Check action items added to lists
6. (Optional) Run `meeting-approve` to mark as complete

### When to Use Each Mode

- **Quick:** In a rush, just need action items
- **Essential:** Standard post-meeting workflow
- **Full:** Important meetings, want complete intelligence

---

## Quality Standards

Every processed meeting includes:

✅ **Full transcript reading** - No truncation  
✅ **Real LLM analysis** - Not placeholder text  
✅ **Specific action items** - With owners, deadlines, priorities  
✅ **Strategic insights** - Hiring, product, personal themes  
✅ **Relationship intelligence** - What to follow up on  
✅ **Draft communications** - Follow-up email ready to send

Same quality as manual processing, but fully automated.

---

## Related Commands & Documentation

**After meeting processing:**
```bash
# Approve meeting outputs
N5: meeting-approve <meeting_folder_name>

# Search previous meetings
N5: meeting-search --stakeholder logan-currie

# Generate cross-meeting insights
N5: meeting-summary --stakeholder logan-currie --last 3
```

**Quick Links:**
- **Full Architecture:** `file 'N5/System Documentation/MEETING_SYSTEM_ARCHITECTURE.md'`
- **Changelog:** `file 'N5/System Documentation/MEETING_PROCESS_CHANGELOG.md'`
- **Command Docs:** `file 'N5/commands/meeting-process.md'`
- **Schemas:** `file 'N5/schemas/meeting-metadata.schema.json'`

---

**Version:** 3.0  
**Last Updated:** 2025-10-10  
**Status:** ✅ Production Active
