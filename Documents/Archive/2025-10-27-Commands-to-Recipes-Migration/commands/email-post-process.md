---
description: "Validate, extract, and save follow-up email body; enforce output-only contract"
tags: [email, postprocess, guardrails]
---

# Command: email-post-process

Usage:

```bash
command 'email-post-process' for "<meeting_id>"
```

Behavior:
- Reads raw generator output from `RAW/EMAIL.md` inside meeting folder
- Validates with `file 'N5/scripts/email_validator.py'`
- Writes clean body to `DELIVERABLES/follow_up_email_copy_paste.txt`
- Logs to `LOGS/email_postprocess.log`
- Fails if artifacts detected or body < 120 words

Outputs:
- `DELIVERABLES/follow_up_email_copy_paste.txt`
- `LOGS/email_postprocess.log`

Integration:
- Called by `meeting-process.md` final step (external meetings)
