# `email-post-process`

**Version:** 1.0.0  
**Category:** Meeting Intelligence  
**Script:** `N5/scripts/n5_email_post_processor.py`  
**Purpose:** Generate follow-up email after meeting processing completes

---

## Overview

Automatically called after `meeting-process` completes. Generates follow-up email drafts for external stakeholder meetings and returns structured output for SMS notification.

**Integration:** Added as FINAL STEP in `command 'meeting-process'` (v5.1.0)

---

## When It Runs

**Automatically after:** `meeting-process` command completes  
**Manual trigger:** `python3 N5/scripts/n5_email_post_processor.py "<meeting-name>"`

---

## What It Does

1. **Detects meeting type** (external vs internal)
2. **Checks for existing email** (idempotent)
3. **Generates draft if needed** (calls `n5_follow_up_email_generator.py`)
4. **Returns JSON result** (for SMS notification by Zo)

---

## Usage

### Via Zo (Automatic)

After completing `meeting-process`:

```
command 'email-post-process' for "2025-10-10_hamoon-ekhtiari-futurefit"
```

**Zo will:**
1. Execute script
2. Parse JSON output
3. Send SMS notification with results

### Manual CLI

```bash
# Process specific meeting
python3 N5/scripts/n5_email_post_processor.py "2025-10-10_hamoon-ekhtiari-futurefit"

# JSON output (for automation)
python3 N5/scripts/n5_email_post_processor.py "hamoon" --json

# Dry run
python3 N5/scripts/n5_email_post_processor.py "hamoon" --dry-run
```

---

## Output Format

### JSON Structure

```json
{
  "status": "success|exists|skipped|error",
  "meeting": "2025-10-10_hamoon-ekhtiari-futurefit",
  "output_files": [
    "N5/records/meetings/.../DELIVERABLES/follow_up_email_draft.md",
    "N5/records/meetings/.../DELIVERABLES/follow_up_email_copy_paste.txt"
  ],
  "errors": [],
  "message": "Email draft generated successfully"
}
```

### Status Codes

- **success:** Email generated successfully
- **exists:** Email already exists (idempotent)
- **skipped:** Internal meeting (no follow-up needed)
- **error:** Generation failed

---

## SMS Notifications

**Zo sends SMS based on status:**

**If status = "success":**
```
✅ Follow-up email ready: {meeting_name}

Draft: DELIVERABLES/follow_up_email_copy_paste.txt

Review and send when ready!
```

**If status = "exists":**
No SMS needed (already notified)

**If status = "skipped":**
No SMS needed (internal meeting)

**If status = "error":**
```
❌ Email generation failed: {meeting_name}

Error: {error_details}

Run manually: python3 N5/scripts/n5_email_post_processor.py "{meeting}"
```

---

## Features

✅ **Auto-detect external meetings** (`_external-` prefix)  
✅ **Idempotent** (won't regenerate existing drafts)  
✅ **Fuzzy matching** (partial meeting names work)  
✅ **Timeout protection** (120s max)  
✅ **Error handling** (graceful failures)  
✅ **JSON output** (automation-friendly)

---

## Examples

### Success Case
```bash
$ python3 N5/scripts/n5_email_post_processor.py "hamoon"

✅ Email generated: 2025-10-10_hamoon-ekhtiari-futurefit
   📄 N5/records/meetings/.../DELIVERABLES/follow_up_email_draft.md
   📄 N5/records/meetings/.../DELIVERABLES/follow_up_email_copy_paste.txt
```

### Already Exists
```bash
✓ Email already exists: 2025-10-10_hamoon-ekhtiari-futurefit
   📄 N5/records/meetings/.../DELIVERABLES/follow_up_email_draft.md
```

### Internal Meeting
```bash
⏭️  Skipped: 2025-08-27_internal-team
   Internal meeting (no follow-up needed)
```

---

## Integration Points

- **Parent:** `command 'meeting-process'` (v5.1.0)
- **Calls:** `N5/scripts/n5_follow_up_email_generator.py`
- **Spec:** `command 'follow-up-email-generator'` (v11.0.1)

---

## Related Commands

- `command 'meeting-process'` — Full meeting processing pipeline (parent)
- `command 'follow-up-email-generator'` — Standalone email generation

---

**Created:** 2025-10-13  
**Status:** ✅ Production Ready  
**Auto-trigger:** After meeting-process completes
