---
description: Daily digest tracking generated follow-up emails that haven't been sent
tool: true
  yet. Scans meeting folders for follow-up emails and checks Gmail to identify which
  ones are still pending.
tags: []
---
# unsent-followups-digest

**Category:** Communication  
**Version:** 1.0.0  
**Created:** 2025-10-13

---

## Purpose

Daily digest tracking generated follow-up emails that haven't been sent yet. Scans meeting folders for follow-up emails and checks Gmail to identify which ones are still pending.

---

## Usage

```bash
# Run digest (outputs to N5/logs/)
python3 /home/workspace/N5/scripts/n5_unsent_followups_digest.py

# Dry run (preview without saving)
python3 /home/workspace/N5/scripts/n5_unsent_followups_digest.py --dry-run

# Debug mode (verbose logging)
python3 /home/workspace/N5/scripts/n5_unsent_followups_digest.py --debug
```

---

## How It Works

1. **Scans meetings** in `N5/records/meetings/` for external meetings with generated follow-ups
2. **Checks Gmail** sent folder for matching emails (subject + recipient fuzzy match)
3. **Filters declined** follow-ups (marked via `drop-followup` command)
4. **Generates digest** sorted FIFO (oldest meetings first)
5. **Saves to** `N5/logs/unsent_followups_digest_{timestamp}.md`

---

## Digest Format

For each unsent follow-up:
- Stakeholder name
- Meeting date (days ago)
- Subject line
- Email address
- Action required (from deliverable map)
- Link to draft file
- Drop command

---

## Scheduled Execution

**Schedule:** Daily at 08:00 ET (including weekends)  
**Delivery:** Email notification  
**Behavior:** Skips if no unsent follow-ups

---

## Related Commands

- `drop-followup` — Mark follow-up as declined
- `follow-up-email-generator` — Generate new follow-up emails

---

## Technical Details

### Dependencies
- Meeting metadata in `_metadata.json`
- Follow-up deliverables in `DELIVERABLES/` folder
- Gmail API (future - Phase 2)

### Exit Codes
- `0` — Success
- `1` — Error

### Logs
- Output: `N5/logs/unsent_followups_digest_{timestamp}.md`
- Debug: Use `--debug` flag

---

**Status:** Active (Gmail integration enabled)  
**Maintainer:** N5 System
