# `meeting-approve`

**Version:** 3.0.0  
**Category:** Meeting Intelligence  
**Script:** `N5/scripts/n5_meeting_approve.py`  
**Purpose:** Approve meeting outputs and trigger downstream actions including auto-email generation

---

## Overview

Approve processed meetings and trigger downstream actions:
- ✅ **Auto-generate follow-up emails** (external meetings only)
- Review generated deliverables
- Send email drafts (copy-paste to Gmail)
- Update CRM (future)
- Schedule follow-up meetings (future)

**New in v3.0:** Automatically detects external stakeholder meetings and generates follow-up email drafts immediately, with SMS notification upon completion.

---

## Quick Start

```bash
# Process meeting with auto-email generation (external meetings)
python3 N5/scripts/n5_meeting_approve.py "hamoon"

# Dry-run first (recommended)
python3 N5/scripts/n5_meeting_approve.py "2025-10-10_hamoon-ekhtiari-futurefit" --dry-run

# Skip auto-email generation
python3 N5/scripts/n5_meeting_approve.py "hamoon" --no-auto-email

# Trigger all downstream actions
python3 N5/scripts/n5_meeting_approve.py "hamoon" --actions all
```

---

## What Happens Automatically

### For External Meetings

1. ✅ **Detects external stakeholder** (3-way check):
   - Meeting ID contains `_external-`
   - `stakeholder_profile.md` exists
   - `_metadata.json` has `stakeholder_classification: external`

2. ✅ **Generates email draft** (if not exists):
   - Calls `n5_follow_up_email_generator.py`
   - Outputs to `DELIVERABLES/follow_up_email_copy_paste.txt`
   - Uses v11.0.1 specification (13-step pipeline)
   - 5-minute timeout protection

3. ✅ **Sends SMS notification**:
   - Queues notification to `N5/inbox/notifications/`
   - Includes meeting name + file location
   - Success or failure message

4. ✅ **Idempotent**:
   - Won't regenerate if draft already exists
   - Safe to run multiple times

### For Internal Meetings

- ⏭️ **Skips email generation** (logged)
- Other actions proceed normally

---

## Usage

### Basic Approval

```bash
# Approve meeting (auto-email for external)
python3 N5/scripts/n5_meeting_approve.py "meeting-name"

# Examples (partial name matching works):
python3 N5/scripts/n5_meeting_approve.py "hamoon"
python3 N5/scripts/n5_meeting_approve.py "2025-10-10_hamoon"
```

### With Options

```bash
# Preview without executing
python3 N5/scripts/n5_meeting_approve.py "hamoon" --dry-run

# Skip automatic email generation
python3 N5/scripts/n5_meeting_approve.py "hamoon" --no-auto-email

# Specific actions only
python3 N5/scripts/n5_meeting_approve.py "hamoon" --actions send_email
python3 N5/scripts/n5_meeting_approve.py "hamoon" --actions send_email update_crm

# All downstream actions
python3 N5/scripts/n5_meeting_approve.py "hamoon" --actions all
```

---

## CLI Flags

| Flag | Description |
|------|-------------|
| `meeting_folder` | Meeting name or ID (partial match supported) |
| `--actions` | Actions to trigger: `send_email`, `update_crm`, `schedule_followup`, `all` |
| `--no-auto-email` | Skip automatic email generation for external meetings |
| `--dry-run` | Preview actions without executing |
| `--generate-missing` | Auto-generate missing deliverables (reserved for future) |

---

## Output

### Console Output

```
======================================================================
MEETING: 2025-10-10_hamoon-ekhtiari-futurefit
======================================================================

📦 Deliverables Status:
  ✅ follow_up_email
  ❌ blurb
  ❌ one_pager
  ❌ proposal

🎯 Requested Actions: send_email

======================================================================
APPROVAL SUMMARY
======================================================================

✅ Email Draft Generated
   📄 /home/workspace/N5/records/meetings/.../DELIVERABLES/follow_up_email_copy_paste.txt

✅ Completed: send_email
```

### SMS Notification

#### Success
```
✓ Follow-up email draft ready: 2025-10-10_hamoon-ekhtiari-futurefit

Location: DELIVERABLES/follow_up_email_copy_paste.txt
```

#### Failure
```
⚠️ Email generation failed: 2025-10-10_hamoon-ekhtiari-futurefit

Check N5/logs/ for details.
```

---

## Integration Flow

### Automatic (Post-Meeting Processing)

```
Transcript → meeting_auto_processor.py
         ↓
    Zo processes meeting (command 'meeting-process')
         ↓
    Blocks + stakeholder profile generated
         ↓
    meeting_approve.py called automatically
         ↓
    Detects external meeting → Generates email
         ↓
    SMS notification sent
         ↓
    User reviews draft manually
```

### Manual (On-Demand)

```
User runs: meeting-approve "hamoon"
         ↓
    Detects external → Generates email
         ↓
    SMS notification sent
         ↓
    User reviews draft
```

---

## File Locations

### Input
- Meeting folder: `N5/records/meetings/{meeting_id}/`
- Required blocks: `B01`, `B08`, `B25`, `stakeholder_profile.md`

### Output
- Email draft: `N5/records/meetings/{meeting_id}/DELIVERABLES/follow_up_email_copy_paste.txt`
- Full draft: `N5/records/meetings/{meeting_id}/DELIVERABLES/follow_up_email_draft.md`
- Artifacts: `N5/records/meetings/{meeting_id}/DELIVERABLES/follow_up_email_artifacts.json`
- SMS queue: `N5/inbox/notifications/sms_{timestamp}_{meeting_name}.json`

### Logs
- Script logs: `N5/logs/meeting-approve.log`
- Email generator logs: Standard output/error

---

## Troubleshooting

### Email Not Generated

**Symptoms:** `⏭️ Email Generation Skipped: internal meeting`

**Cause:** Meeting not detected as external

**Fix:**
1. Check meeting folder name contains `_external-`
2. Verify `stakeholder_profile.md` exists
3. Check `_metadata.json` has correct classification

### Generation Timeout

**Symptoms:** `❌ Email generation failed: Generation timeout (>5 min)`

**Cause:** Email generator hung or very slow

**Fix:**
1. Check meeting folder has all required blocks
2. Verify transcript exists and is readable
3. Run generator manually to debug: `python3 N5/scripts/n5_follow_up_email_generator.py /path/to/meeting`

### Duplicate Emails

**Symptoms:** Multiple email drafts generated

**Resolution:** System is idempotent and checks for existing drafts. This should not happen. If it does:
1. Check file permissions on DELIVERABLES/
2. Verify idempotent check is working: `ls -la DELIVERABLES/follow_up_email*`

---

## Safety Features

- ✅ **Idempotent:** Won't regenerate existing drafts
- ✅ **Dry-run support:** Preview without execution
- ✅ **Timeout protection:** 5-minute cap on generation
- ✅ **Error handling:** All subprocess calls protected
- ✅ **Logging:** Comprehensive logs to N5/logs/
- ✅ **Manual review required:** Never auto-sends emails
- ✅ **SMS notifications:** Alerts on success/failure

---

## Related Commands

- `command 'meeting-process'` — Process meeting transcript into intelligence blocks
- `command 'follow-up-email-generator'` — Standalone email generator (v11.0.1)
- `command 'aggregate-insights'` — Aggregate B31 insights across meetings

---

## Version History

- **v3.0.0** (2025-10-13): Added auto-email generation for external meetings + SMS notifications
- **v2.0.0** (2025-10-13): Enhanced with downstream actions framework
- **v1.0.0** (2025-09): Initial meeting approval script

---

**Last Updated:** 2025-10-13  
**Maintained By:** Vrijen Attawar  
**Status:** ✅ Production Ready
