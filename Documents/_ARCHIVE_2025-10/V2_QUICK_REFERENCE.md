# V2 Meeting Orchestrator - Quick Reference Guide

## Basic Usage

### Process a Text Transcript
```bash
python3 N5/scripts/meeting_orchestrator.py transcript.txt --type sales
```

### Process a Word Document (.docx)
```bash
python3 N5/scripts/meeting_orchestrator.py transcript.docx --type fundraising
```

### Specify Multiple Meeting Types
```bash
python3 N5/scripts/meeting_orchestrator.py transcript.txt \
    --type sales partnership \
    --stakeholder external
```

## Meeting Types

Use these values with the `--type` flag:
- `sales` - Sales calls, demos, prospecting
- `fundraising` - Investor pitches, VC meetings
- `partnership` - Partnership discussions, collaborations
- `community_partnerships` - Community organization partnerships
- `coaching` - 1-on-1 coaching sessions
- `general` - Default for other types

## Stakeholder Types

Use these values with the `--stakeholder` flag:
- `external` - External stakeholders (investors, partners, clients)
- `internal` - Internal team members
- `candidate` - Coaching clients/candidates

## Output Structure

Each processed meeting creates a directory:
```
Careerspan/Meetings/YYYY-MM-DD_HHMM_type_stakeholder/
├── transcript.txt                  # Original transcript
├── REVIEW_FIRST.md                 # ⭐ START HERE - Quick dashboard
├── content-map.md                  # Extraction details
├── RECOMMENDED_DELIVERABLES.md     # What to generate next
├── _metadata.json                  # Processing metadata
├── INTELLIGENCE/
│   ├── action-items.md             # Extracted actions
│   ├── decisions.md                # Extracted decisions
│   └── detailed-notes.md           # Key insights
└── DELIVERABLES/                   # (Phase 4 - future)
```

## Workflow

1. **Process Meeting**
   ```bash
   python3 N5/scripts/meeting_orchestrator.py meeting.txt --type sales
   ```

2. **Review Outputs**
   - Check `REVIEW_FIRST.md` for quick summary
   - Review action items in `INTELLIGENCE/action-items.md`
   - Check decisions in `INTELLIGENCE/decisions.md`

3. **Check Recommendations**
   - Open `RECOMMENDED_DELIVERABLES.md`
   - See what deliverables are recommended (blurb, email, memo, etc.)

4. **Generate Deliverables** (Phase 4 - coming soon)
   ```bash
   # Future command
   N5: generate-deliverables "folder-name" --deliverables blurb,follow_up_email
   ```

## Notification

After processing, you'll receive a simulated SMS notification (logged) with:
- Meeting name
- Action item count
- Decision count
- Recommended deliverables
- Direct link to review outputs

Example:
```
Meeting processed: Sarah Chen

1 action items, 0 decisions

Recommended: blurb, follow up email

Review: https://va.zo.computer/workspace/Careerspan/Meetings/2025-10-10_1400_sales_sarah-chen
```

## What Gets Extracted

### Automatically Detected
- ✅ Participant names
- ✅ Company/organization names
- ✅ Meeting date and time
- ✅ Primary stakeholder
- ✅ Action items with owners and deadlines
- ✅ Decisions made
- ✅ Key insights and advice

### Intelligently Recommended
Based on meeting type and content:
- **Blurbs** - For external meetings (sales, fundraising)
- **Follow-up Emails** - When action items exist
- **One-Pager Memos** - For strategic discussions
- **Stakeholder Profiles** - For new relationships

## Tips

1. **Transcript Format**
   - Works best with speaker labels: `Name: statement`
   - Supports both .txt and .docx files
   - Include meeting date/time in transcript header if available

2. **Meeting Types Matter**
   - More specific types = better recommendations
   - Can specify multiple types for hybrid meetings
   - Example: `--type sales partnership`

3. **Review Intelligence Blocks**
   - Always check `INTELLIGENCE/` folder for detailed extractions
   - Action items include owners and deadlines
   - Decisions include rationale and context

4. **Fallback Behavior**
   - System gracefully handles LLM failures
   - Falls back to simple extraction if needed
   - Never crashes - always produces output

## Files

- **Main Script**: `N5/scripts/meeting_orchestrator.py`
- **Backup**: `N5/scripts/meeting_orchestrator_BACKUP_20251010_132417.py`
- **Test Transcript**: `test_transcript.txt`

## Common Issues

### Pandoc Not Found
```bash
apt-get install -y pandoc
```

### No Participants Detected
- Check transcript format
- Ensure speaker labels: `Name: statement`

### Wrong Recommendations
- Specify meeting type explicitly with `--type`
- Example: `--type sales` instead of relying on auto-detection

## Status

- ✅ Phase 1: Essential Intelligence Generation - **COMPLETE**
- ✅ Phase 2: Smart Recommendations - **COMPLETE**
- 🔄 Phase 3: Wait for User Request - **READY**
- 🔄 Phase 4: On-Demand Generation - **INFRASTRUCTURE READY**

Last Updated: October 10, 2025
