---
title: X Thought Leader
description: Interactive interface to the X Thought Leadership Engine. Monitor accounts, generate engagement drafts, manage approvals, analyze voice patterns.
tags:
  - x
  - twitter
  - social
  - thought-leadership
  - engagement
tool: true
---
# X Thought Leadership Engine

Reactive engagement system that monitors X accounts for tweets correlating with your positions, generates 4-variant responses, and posts with your approval.

## Quick Commands

| Command | What it does |
|---------|--------------|
| `status` | Full system status |
| `poll` | Fetch new tweets from monitored accounts |
| `pending` | Show tweets ready for drafting |
| `run` | Execute full pipeline |

## Detailed Commands

### System Status

**Full status:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/orchestrator.py status
```

**Just pending drafts:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/draft_generator.py --list-ready --min-score 0.3
```

### Polling & Correlation

**Poll all accounts:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/polling_agent.py --force
```

**Poll specific account:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/polling_agent.py --force --account asanwal
```

**Run correlation on new tweets:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/correlator.py --min-score 0.3
```

### Draft Generation

**Generate drafts for a tweet:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/draft_generator.py --tweet-id <TWEET_ID>
```

**Format for SMS preview:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/draft_generator.py --format-sms <TWEET_ID>
```

### Account Management

**List monitored accounts:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/polling_agent.py --list-accounts
```

**Add account:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/add_account.py <username> --notes "<category>"
```

### Posting

**Check pending approvals:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/poster.py pending
```

**Post approved tweet (dry-run first):**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/poster.py post <TWEET_ID> <VARIANT> --dry-run
python3 /home/workspace/Projects/x-thought-leader/src/poster.py post <TWEET_ID> <VARIANT>
```
Variants: `supportive`, `challenging`, `spicy`, `comedic` (or 1-4)

### Voice Learning

**Selection stats:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/voice_learner.py stats --days 30
```

**Performance analysis:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/voice_learner.py performance --days 30
```

**Analyze voice samples:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/voice_learner.py analyze
```

**Get recommendations:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/voice_learner.py recommend
```

**Full report:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/voice_learner.py report
```

### Testing & Debugging

**Test position matching:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/position_matcher.py match "The biggest problem in hiring is signal quality"
```

**Check tweet statuses:**
```bash
sqlite3 /home/workspace/Projects/x-thought-leader/db/tweets.db "SELECT status, COUNT(*) FROM tweets GROUP BY status"
```

**View recent drafts:**
```bash
sqlite3 /home/workspace/Projects/x-thought-leader/db/tweets.db "SELECT tweet_id, variant, substr(content, 1, 60) FROM drafts ORDER BY created_at DESC LIMIT 10"
```

## Full Pipeline

The complete flow:
1. **Poll** — Fetch new tweets from monitored accounts
2. **Correlate** — Score against positions.db (threshold: 0.3)
3. **Draft** — Generate 4 variants for qualifying tweets
4. **SMS** — Send to V for approval (8am-10pm ET)
5. **Post** — Post approved variant as reply
6. **Learn** — Track selection for voice refinement

**Run everything:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/orchestrator.py run --force
```

## Voice Variants

| # | Variant | Style |
|---|---------|-------|
| 1 | supportive | Build rapport, agree and amplify |
| 2 | challenging | Respectful pushback, alternative view |
| 3 | spicy | Bold takes, high-signal contrarian |
| 4 | comedic | Wit, absurdist, memorable |

## SMS Approval Format

When you receive a draft SMS:
- Reply `1`, `2`, `3`, or `4` to select that variant
- Reply `0` or `skip` to pass
- Reply `3: make it spicier` to request regeneration with feedback

## Files

- Database: `Projects/x-thought-leader/db/tweets.db`
- Voice config: `Projects/x-thought-leader/config/voice_variants.yaml`
- Voice examples: `Projects/x-thought-leader/config/voice_examples.md`
- Positions: `N5/data/positions.db` (105 positions)
- Learning log: `Projects/x-thought-leader/config/learning_log.jsonl`

## Execution

When invoked, parse the user's intent and run the appropriate command from above. For multi-step operations like "run the full pipeline," execute the orchestrator with appropriate flags.


