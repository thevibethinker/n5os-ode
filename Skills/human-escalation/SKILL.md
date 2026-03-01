---
created: 2026-02-10
last_edited: 2026-02-10
version: 1.0
provenance: con_ShvJ5HyUhiehkyDu
name: human-escalation
description: Notify V via SMS when human decision input is needed during autonomous operations. Integrates with pending_decisions store to send formatted notifications with decision context and reminder logic based on priority levels.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  build: zoputer-autonomy-v2
  drop: D3.2
---

# Human Escalation Skill

Notify V via SMS when autonomous operations require human decision input.

## Purpose

When either va or zoputer (or both) have low confidence on a decision (< 0.5), this skill escalates to V for human judgment. This is the notification layer of the Human-in-the-Loop (HITL) system.

## When to Use

- A pending decision exists in the store with status `pending`
- Autonomous workflows need human input before proceeding
- Critical decisions require explicit human approval
- Confidence thresholds are not met for autonomous action

## Integration

This skill integrates with:
- **pending_decisions store** (`N5/scripts/pending_decisions.py`) - Source of decisions needing notification
- **SMS capability** (`send_sms_to_user`) - Delivery mechanism
- **Scheduled agents** - For periodic checking and reminders

## Usage

### Send notification for a specific decision:
```bash
python3 Skills/human-escalation/scripts/notify.py send <decision_id>
```

### Check for decisions needing notification:
```bash
python3 Skills/human-escalation/scripts/notify.py check
```

### View notification status:
```bash
python3 Skills/human-escalation/scripts/notify.py status
```

### Force immediate reminder:
```bash
python3 Skills/human-escalation/scripts/notify.py remind <decision_id>
```

## Orchestrator Script

The orchestrator at `N5/scripts/escalation_notifier.py` provides a higher-level interface:

```bash
python3 N5/scripts/escalation_notifier.py check   # Check and send pending
python3 N5/scripts/escalation_notifier.py send <id>  # Force send specific
python3 N5/scripts/escalation_notifier.py status  # Show notification status
```

## SMS Format

Messages follow a compact format (< 160 chars):

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

| Priority | Reminders |
|----------|-----------|
| low      | None |
| normal   | None (initial only) |
| high     | 6h before expiry |
| critical | 2h and 1h before expiry |

## Response Handling

V can respond via SMS with:
- `n5 decision <short_id>` - View full context
- `n5 decision <short_id> approve` - Approve the action
- `n5 decision <short_id> reject` - Reject the action
- `n5 decision <short_id> <custom response>` - Provide custom resolution

Note: Response handling is implemented by D3.3 (SMS Decision Resolver).

## Files

- `SKILL.md` - This documentation
- `scripts/notify.py` - Core notification logic
- `N5/scripts/escalation_notifier.py` - Orchestrator script
