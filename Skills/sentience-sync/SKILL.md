---
name: sentience-sync
description: |
  Two-way sync with Sentience API. Manages three processes: (1) Push curated Zo memories to Sentience with PII filtering,
  (2) Poll for new memories and stream desktop screenshots to a local activity feed, (3) Daily digest agent that
  categorizes activity into buckets (personal, work-project, zo, physical-intelligence, other) using a relevance rubric.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.1"
---

# Sentience Sync

## Architecture

```
Sentience API ←→ [PULL] pull_memories.py ←→ [AGENT: 6h SMS if interesting]
              ←→ [FEED] activity_feed.py ←→ [AGENT: 30min SILENT] → activity_feed.jsonl (48h rolling)
              ←→ [DIGEST] daily_digest.py ←→ [AGENT: daily 9PM PT SMS]

Sentience API ← [PUSH] push_memories.py ← Zo workspace
               (PII-filtered, idempotent via push ledger)
```

## Key Design Decisions

- **Per-stream seen tracking**: `seen_store.json` tracks pull and activity_feed streams separately (no cross-contamination)
- **Atomic writes**: all JSON state files use `write→rename` pattern (no corruption on concurrent writes)
- **Push idempotency**: `push_ledger.json` tracks pushed content by hash — safe to re-run without duplicates
- **PII scrubbing**: 19 regex patterns strip emails, phones, addresses, API keys, meeting URLs before any external write
- **Timezone-aware**: digest uses PT day boundaries for 9PM daily summary
- **Source-aware classification**: screenshots classified by app + window + structured facts; emails by sender domain + subject

## Processes

| Process | Script | Schedule | Delivery | Purpose |
|---------|--------|----------|----------|---------|
| **Push** | `scripts/push_memories.py` | Manual | — | Push Zo knowledge → Sentience (PII-scrubbed, idempotent) |
| **Pull** | `scripts/pull_memories.py` | Every 6h | SMS if interesting | Surface new non-Zo memories |
| **Activity Feed** | `scripts/activity_feed.py` | Every 30 min | Silent | Stream screenshots → 48h local feed |
| **Daily Digest** | `scripts/daily_digest.py` | Daily 9PM PT | SMS | Categorized day summary + commitments |

## Scripts

```bash
# Push Zo memories to Sentience (idempotent — skips already-pushed)
python3 Skills/sentience-sync/scripts/push_memories.py [--dry-run]

# Pull new memories (auto-runs every 6h via agent)
python3 Skills/sentience-sync/scripts/pull_memories.py [--hours N] [--dry-run]

# Update activity feed (auto-runs every 30min via agent)
python3 Skills/sentience-sync/scripts/activity_feed.py [--hours N]

# Generate daily digest (auto-runs daily 9PM PT via agent)
python3 Skills/sentience-sync/scripts/daily_digest.py --date YYYY-MM-DD [--hours N]
```

## Shared Modules

| Module | Purpose |
|--------|---------|
| `scripts/state.py` | `SeenStore` (per-stream dedup), `WatermarkStore` (high-water marks), `PushLedger` (idempotency) |
| `scripts/pii.py` | 19 PII patterns — emails, phones, addresses, API keys, JWTs, meeting URLs, SSNs, card data |

## Data Files

| File | Purpose |
|------|---------|
| `data/seen_store.json` | Per-stream seen ID tracking (TTL: 30 days) |
| `data/watermarks.json` | High-water marks per stream |
| `data/push_ledger.json` | Idempotency — tracks pushed content by hash |
| `data/activity_feed.jsonl` | Rolling 48h activity log from screenshots |
| `data/last_pull.json` | Last pull timestamp |
| `data/relevance_rubric.yaml` | Bucket keywords + priority scoring rules |
| `data/digests/YYYY-MM-DD.json` | Daily digest outputs |

## Relevance Rubric

See `file 'Skills/sentience-sync/data/relevance_rubric.yaml'` for full rules.

### Buckets

| Bucket | Key signals |
|--------|-------------|
| **work-project** | Coaching, clients, Work Project app, hiring keywords, Superhuman/Calendly |
| **zo** | Zo, N5, agent, skill, workspace, zosite, pulse |
| **physical-intelligence** | Hospital data, embodied AI, robotics, sensors, Anna, training data |
| **personal** | Messages, WhatsApp, health, family, travel |
| **other** | Everything else |

### Priority Scoring

- **HIGH**: Commitments ("agreed to", "by EOD"), decisions made, money sent
- **MEDIUM_HIGH**: Met someone new, shipped/created something, received offer
- **MEDIUM**: New ideas, research, feedback reviewed
- **LOW**: Routine triage, calendar browsing, general reading
- **SKIP**: System notifications, lock screen, duplicate captures

## Configuration

Requires `SENTIENCE_API_KEY` in [Settings > Advanced](/?t=settings&s=advanced).

## Debugging

```bash
# Test all scripts with dry-run
python3 Skills/sentience-sync/scripts/pull_memories.py --dry-run
python3 Skills/sentience-sync/scripts/activity_feed.py --dry-run
python3 Skills/sentience-sync/scripts/daily_digest.py --hours 24 --output markdown
python3 Skills/sentience-sync/scripts/push_memories.py --dry-run

# Check state
python3 -c "
import sys; sys.path.insert(0,'Skills/sentience-sync/scripts')
from state import SeenStore, PushLedger
s = SeenStore(); print('SeenStore streams:', list(s._data['streams'].keys()))
p = PushLedger(); print('PushLedger:', p.count(), 'entries')
"