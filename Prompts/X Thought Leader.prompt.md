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
version: 1.1
last_edited: 2026-01-12
---
# X Thought Leadership Engine

Reactive engagement system that monitors X accounts for tweets correlating with your positions, **surfaces angles to spark your creativity**, and drafts only as backup when you provide direction.

**Philosophy:** Build the muscle, don't outsource the creative work. The system curates and sparks — you write.

## Quick Commands

| Command | What it does |
|---------|--------------|
| `status` | Full system status |
| `poll` | Fetch new tweets from monitored accounts |
| `pending` | Show tweets worth engaging with |
| `angles <id>` | **PRIMARY:** Get angles/hooks for a tweet |
| `draft <id> "your spark"` | **BACKUP:** Draft based on your direction |
| `run` | Execute full pipeline |
| `pangram` | Test output against AI detection |

## Primary Workflow: Angles First

**The system surfaces opportunities and sparks. You write.**

### 1. See what's pending
```bash
python3 /home/workspace/Projects/x-thought-leader/src/angles_generator.py --pending
```

Output:
```
📋 PENDING TWEETS (5 with score >= 0.3):

  [a1b2c3d4] @alexandr_wang (87% match, 3 positions)
           "One-click apply destroyed recruiting..."
```

### 2. Get angles for a tweet
```bash
python3 /home/workspace/Projects/x-thought-leader/src/angles_generator.py --tweet-id <ID>
```

Output:
```
═══════════════════════════════════════════════════════
📣 @alexandr_wang:
"One-click apply destroyed recruiting..."

📍 POSITION MATCHES:
   • Hiring signal degradation (87%)
   • Application friction as feature (72%)

🎯 ANGLES:
   [FLIP] One-click isn't the disease, it's the symptom
      → The real problem is employers optimizing for volume over signal...

   [LIVED] 10 years coaching people who can't articulate what they want
      → If candidates can't answer "why this role" they shouldn't apply...

   [SPICY] "If Alexandr Wang thinks parenting is hard, try screening 10k resumes"
      → Scale AI built their moat on data quality. Ironic to miss this in hiring...

   [PROXY] Responsiveness as proxy for self-knowledge
      → Inbox management = role management. 24 hours isn't lag, it's signal...

🌍 CULTURAL MOMENTS:
   • "Vibe coding" discourse: Connect to vibe-based hiring?
   • Recent layoff waves: Signal quality matters more when hiring slows

═══════════════════════════════════════════════════════
💡 Pick an angle, riff on it. Draft backup: provide your spark.
```

### 3. Write your tweet (primary path)
Use the angles to spark your own response. This builds the muscle.

### 4. Draft from your spark (backup only)
If you want system help, provide YOUR direction first:
```bash
python3 /home/workspace/Projects/x-thought-leader/src/angles_generator.py --tweet-id <ID> --draft "the responsiveness proxy angle — tie to inbox = role management"
```

The system drafts based on YOUR spark, not its own ideas.

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

## Pangram AI Detection

Integrated with Pangram API to validate drafts don't read as AI-generated.

**Test text directly:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/draft_generator.py --pangram-test "your text here"
```

**Check existing draft:**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/draft_generator.py --pangram-check <DRAFT_ID_PREFIX>
```

**Generate with Pangram validation (auto-retry on fail):**
```bash
python3 /home/workspace/Projects/x-thought-leader/src/draft_generator.py --tweet-id <ID> --pangram
```

**Threshold:** `fraction_ai < 0.3` (30%) to pass

**If drafts fail Pangram, apply fixes from:** `file 'N5/prefs/communication/style-guides/pangram-signals.md'`

## Files

- Database: `Projects/x-thought-leader/db/tweets.db`
- Voice config: `Projects/x-thought-leader/config/voice_variants.yaml`
- Voice examples: `Projects/x-thought-leader/config/voice_examples.md`
- Positions: `N5/data/positions.db` (105 positions)
- Learning log: `Projects/x-thought-leader/config/learning_log.jsonl`

## Execution

When invoked, parse the user's intent and run the appropriate command from above. For multi-step operations like "run the full pipeline," execute the orchestrator with appropriate flags.

## Voice Enhancement (Auto-Applied) ⭐ NEW in v1.1

When generating drafts, the system automatically injects V's distinctive linguistic patterns from the Voice Library.

**Implementation:**
```python
from N5.scripts.voice_layer import VoiceContext, inject_voice

ctx = VoiceContext(
    content_type="tweet",
    platform="x",
    purpose="thought-leadership",
    topic_domains=position_domains,  # From matched positions
)

enhanced_prompt = inject_voice(draft_prompt, ctx)
```

**What happens automatically:**
1. Layer retrieves 3 relevant primitives (favoring signature_phrase, metaphor, rhetorical_device)
2. Primitives injected as context into draft generation
3. LLM weaves patterns naturally — never forced
4. Usage tracked to prevent repetition across tweets

**Result:** Drafts incorporate V's distinctive voice patterns without mechanical insertion.

---

## Draft Generation (Backup Mode)


