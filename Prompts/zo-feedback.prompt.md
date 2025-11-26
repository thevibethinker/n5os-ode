---
created: 2025-11-26
last_edited: 2025-11-26
version: 2.0
title: Zo Feedback
description: |
  Send feedback to the Zo team via Slack with Google Drive context folder.
  Respects business hours (9 AM - 6 PM ET Mon-Fri) - messages outside this window are automatically scheduled.
tags: [zo, feedback, slack, communication]
tool: true
---

# Zo Feedback

Send feedback to the Zo team via Slack. Full context and attachments are stored in Google Drive.

## Business Hours

Messages are automatically scheduled to respect the Zo team's time:
- **Window:** 9 AM - 6 PM ET, Monday-Friday
- **Outside hours:** Message is scheduled for next 9 AM ET
- **Override:** Use `--now` flag for urgent issues

## Usage

```bash
# Quick feedback (text only)
python3 N5/scripts/zo_feedback.py -m "Image gen is fast!" -c praise

# With context and screenshot
python3 N5/scripts/zo_feedback.py \
  -m "Button broken on mobile" \
  -x "Tried on iPhone 14, Safari. Steps: 1) Open app 2) Click X 3) See error" \
  -a screenshot.png \
  -c bug -p high

# Force immediate (urgent)
python3 N5/scripts/zo_feedback.py -m "Critical bug" -c bug -p high --now

# Test mode (vrijen-slack-backend)
python3 N5/scripts/zo_feedback.py -m "Testing" --test
```

## Arguments

| Flag | Description |
|------|-------------|
| `-m`, `--message` | **Required.** BLUF summary (appears in Slack) |
| `-x`, `--context` | Full details (saved to Drive markdown) |
| `-a`, `--attachments` | Files to attach (images/videos) |
| `-c`, `--category` | `bug`, `feature`, `ux`, `question`, `praise` |
| `-p`, `--priority` | `high`, `medium`, `low` |
| `--test` | Send to test channel (vrijen-slack-backend) |
| `--now` | Force immediate send (bypass business hours) |

## Output Structure

| Destination | Content |
|-------------|---------|
| **Slack** | BLUF + 📁 link to Drive folder |
| **Drive** | `feedback.md` (full context) + media files |

## Channel Configuration

Edit `N5/scripts/zo_feedback.py` to change channels:

```python
CHANNELS = {
    "production": {"id": "C09NDHKEXEJ", "name": "ext-zo-vrijen"},
    "test": {"id": "C085K7QE17C", "name": "vrijen-slack-backend"}
}
DEFAULT_CHANNEL = "test"  # Change to "production" when ready
```

## Workflow (with attachments)

When attachments or context are provided:
1. Script stages files to `/tmp/zo_feedback_staging/`
2. Creates manifest at `/tmp/zo_feedback_manifest.json`
3. Outputs `__ZO_FEEDBACK_READY__` signal
4. Zo uploads folder to Drive, shares it, sends Slack message

## Supported Files

- **Images:** PNG, JPG, JPEG, GIF, WEBP, BMP
- **Videos:** MP4, MOV, AVI, WEBM, MKV


