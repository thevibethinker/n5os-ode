---
name: human-escalation
description: Notify V via SMS when human decision input is needed during autonomous operations. Integrates with pending_decisions store to send formatted notifications with decision context and reminder logic based on priority levels.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
---

# Human Escalation Skill

Notify V via SMS when human decision input is needed during autonomous operations.

## Purpose

When autonomous operations encounter decisions requiring human judgment, this skill sends SMS notifications to V with:
- Brief decision summary (< 160 chars) 
- Decision priority level
- Reference ID for full context retrieval
- Reminder scheduling based on priority

## Integration Points

- **pending_decisions store**: Reads decision data via `pending_decisions.py`
- **SMS delivery**: Uses Zo's `send_sms_to_user` capability
- **Reminder logic**: Tracks notification state to avoid spam

## Usage

### Direct notification
```bash
python3 Skills/human-escalation/scripts/notify.py <decision_id> [--immediate]
```

### Orchestrated checking
```bash 
python3 N5/scripts/escalation_notifier.py check  # Check all pending
python3 N5/scripts/escalation_notifier.py status  # Show notification state
```

## SMS Format

```
🔔 Decision needed ({priority})
{summary}

Reply: n5 decision {short_id}
```

Example:
```
🔔 Decision needed (high)
Zoputer: Should I remove review gate for ClientX workflow?

Reply: n5 decision d7f3
```

## Reminder Schedule

- **low**: No reminders (initial notification only)
- **normal**: No reminders (initial notification only) 
- **high**: Reminder at 6 hours
- **critical**: Reminders at 2h and 1h before expiry

## Notification State

Tracks whether initial notifications and reminders have been sent to prevent duplicate alerts.

## Files

- `scripts/notify.py`: Core notification logic
- Integrates with `N5/scripts/escalation_notifier.py` for orchestrated checking