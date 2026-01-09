---
created: 2026-01-09
last_edited: 2026-01-09
version: 1
provenance: con_nRtJ8573Bwl836An
status: handoff
---
# X Thought Leader System — Handoff for Next Conversation

## TL;DR — Pick Up Here

**What works:**
- List sync from `https://x.com/i/lists/1703516711629054447` ✅
- 65 monitored accounts including adjacency targets ✅
- Polling agent collects tweets ✅
- Adjacency finder discovers small high-clout accounts ✅
- SMS alerting infrastructure ✅

**What's broken:**
1. **Stage 1 gate is too narrow** — keyword matching rejects most tweets
2. **Reply drafts are generic slop** — voice prompt is made-up bullet points, not V's real voice
3. **Need full semantic gating** — V said "fuck the cost, make it all semantic"

## Next Session TODO

### Priority 1: Semantic Gate (kill keyword filter)
```
File: Projects/x-thought-leader/src/relevance_gate.py

Current: Stage 1 keyword filter → Stage 2 LLM
Needed: ALL tweets go to LLM for semantic relevance scoring

The LLM should ask: "Would V have something interesting to say about this?"
NOT: "Does this contain hiring/AI keywords?"
```

### Priority 2: Real Voice Model
```
Sources to pull V's actual voice:
1. DuckDB: /home/workspace/x-history-pre-jan-8/data.duckdb (has V's tweets)
2. Medium posts: medium.com/@thevibethinker
3. Meeting transcripts: Personal/Meetings/

File to fix: Projects/x-thought-leader/src/reply_generator.py
Variable: V_VOICE_PROMPT (line ~15)

Current prompt is generic. Need to:
- Extract actual V tweet samples
- Analyze his real patterns (not made-up bullet points)
- Build voice model from actual writing
```

### Priority 3: Run Full Pipeline
```bash
cd /home/workspace/Projects/x-thought-leader

# Process all 432 unprocessed tweets through semantic gate
python3 src/relevance_gate.py --process --limit 100

# Generate replies with improved voice
python3 src/reply_generator.py --generate --limit 10

# Check quality
python3 src/reply_generator.py --pending
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
├─────────────────────────────────────────────────────────────────┤
│  X List (SSOT)              Power Mutuals              Adjacency │
│  1703516711629054447        @andruyeung (66K)          Finder    │
│  ↓                          @GunnersSean (414K)        ↓         │
│  list_sync.py               @packyM (350K)             Small     │
│                             + 16 more                  accounts  │
│                                                        in orbit  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  polling_agent.py — Collects tweets from 65 accounts            │
│  DB: Projects/x-thought-leader/db/tweets.db                     │
│  Current: 477 tweets, 432 unprocessed                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  relevance_gate.py — NEEDS REWRITE                              │
│  Current: Keyword filter (too narrow)                           │
│  Needed: Full semantic "would V engage?" scoring                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  reply_generator.py — NEEDS VOICE MODEL                         │
│  Current: Generic bullet-point prompt                           │
│  Needed: Real V voice from tweets/Medium/transcripts            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  alert_dispatcher.py — Works ✅                                  │
│  SMS to V when high-relevance tweet needs reply                 │
│  Daily cap: 8, Quiet hours: 10pm-8am ET                         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Files

| File | Status | Notes |
|------|--------|-------|
| `Projects/x-thought-leader/src/list_sync.py` | ✅ Works | Syncs from X list |
| `Projects/x-thought-leader/src/polling_agent.py` | ✅ Works | Collects tweets |
| `Projects/x-thought-leader/src/adjacency_finder.py` | ✅ Works | Finds small high-clout accounts |
| `Projects/x-thought-leader/src/relevance_gate.py` | ❌ Rewrite | Kill keywords, go full semantic |
| `Projects/x-thought-leader/src/reply_generator.py` | ❌ Rewrite | Need real voice model |
| `Projects/x-thought-leader/src/alert_dispatcher.py` | ✅ Works | SMS infrastructure |
| `Projects/x-thought-leader/config/settings.py` | - | Config constants |
| `Projects/x-thought-leader/db/tweets.db` | - | SQLite database |

## V's Strategic Intent (from this conversation)

1. **Network theory growth**: Use power mutuals as social proof credentializer
2. **Second-order adjacency**: Follow small accounts (500-5K) in power mutual orbit
3. **Reply guy strategy**: 30-50 quality replies/day, AI-assisted
4. **The unlock**: When adjacency targets see V is mutual with @andruyeung (66K), @packyM (350K), they're more likely to engage back
5. **Wide capture → emergent domains**: Don't pre-filter by topic. Capture everything, let domains emerge.

## Scheduled Agents

- **X Thought Leader Radar** (every 2 hours, 8am-9pm ET): Polls accounts, runs gate, generates reply drafts
- Agent ID: `4e974467-26ba-480d-80b8-6cf78bec1f87`

## V's Voice Sources (for next session)

```python
# DuckDB with V's tweets
import duckdb
conn = duckdb.connect('/home/workspace/x-history-pre-jan-8/data.duckdb')
tweets = conn.execute("SELECT * FROM tweets ORDER BY created_at DESC LIMIT 100").fetchall()

# Positions database (V's worldview)
import sqlite3
conn = sqlite3.connect('/home/workspace/N5/data/positions.db')
positions = conn.execute("SELECT title, thesis, domain FROM positions").fetchall()
```

## Conversation ID
`con_nRtJ8573Bwl836An`

