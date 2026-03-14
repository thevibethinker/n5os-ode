---
created: 2026-01-09
worker_id: W12
component: System Orchestrator
status: pending
depends_on: [W6, W9]
---

# W12: System Orchestrator

## Objective
Tie all components together into a cohesive system with CLI and agent interfaces.

## Output Files
- `Projects/x-thought-leader/src/orchestrator.py`
- `Projects/x-thought-leader/cli.py`
- `Prompts/X Engage.prompt.md`

## CLI Interface

```bash
# Manual operations
python cli.py poll                    # Manual poll for new tweets
python cli.py status                  # Show pending approvals, limits
python cli.py add-account @handle     # Add account to monitor
python cli.py remove-account @handle  # Remove account
python cli.py list-accounts           # Show monitored accounts
python cli.py history [--days N]      # Show recent posts
python cli.py voice-report            # Generate voice analysis

# Testing
python cli.py test-api                # Verify X API credentials
python cli.py test-draft "tweet text" # Generate test drafts
python cli.py dry-run                 # Full pipeline without posting
```

## Prompt Interface

```markdown
---
title: X Engage
description: Interact with X Thought Leadership Engine
tags: [social, x, twitter, engagement]
tool: true
---

# X Engage

Commands:
- `@X Engage status` — Show pending approvals, daily limits
- `@X Engage poll` — Check for new tweets from monitored accounts
- `@X Engage add @handle` — Add account to monitor
- `@X Engage history` — Recent engagement history
- `@X Engage voice` — Voice learning report
```

## Agent Registration

Two scheduled agents:

### 1. Polling Agent (every 30 min, 8am-10pm ET)
```python
rrule = "FREQ=MINUTELY;INTERVAL=30;BYHOUR=8,9,10,11,12,13,14,15,16,17,18,19,20,21"
instruction = """
Run the X Thought Leadership polling cycle:
1. Execute: python /home/workspace/Projects/x-thought-leader/src/poller.py
2. If new high-correlation tweets found, drafts will be generated
3. Send SMS approval requests for any new draft sets
4. Log results
"""
```

### 2. Voice Learning Agent (weekly, Sunday 9pm)
```python
rrule = "FREQ=WEEKLY;BYDAY=SU;BYHOUR=21;BYMINUTE=0"
instruction = """
Run weekly voice learning cycle:
1. Execute: python /home/workspace/Projects/x-thought-leader/src/voice_learner.py analyze
2. Review approved vs skipped patterns
3. Update learned_voice.yaml
4. Generate report and email to V
"""
```

## System Health Checks

```python
def health_check() -> dict:
    """
    Verify all system components working:
    - X API credentials valid
    - Database accessible
    - Rate limits not exhausted
    - Agents registered and running
    """
```

## Acceptance Criteria
- [ ] CLI provides all manual operations
- [ ] Prompt interface registered and working
- [ ] Polling agent registered (30min, active hours)
- [ ] Voice learning agent registered (weekly)
- [ ] Health check catches issues
- [ ] All components integrate correctly
