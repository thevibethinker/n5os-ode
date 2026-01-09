---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_S4D4PEMvW09h9VCl
---

# X Thought Leadership Engine — Build Orchestration Plan

## Project Summary

**Goal**: Reactive thought leadership system that monitors X accounts, correlates tweets with V's positions, generates 4-variant drafts, and enables SMS-based HITL approval for posting.

**Seed Account**: @asanwal (Anand Sanwal, CB Insights founder)
**Posting Account**: @thevibethinker
**Approval Hours**: 8 AM - 10 PM ET
**API Tier**: X Basic ($200/mo)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         X THOUGHT LEADERSHIP ENGINE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐       │
│   │  W6      │     │  W3      │     │  W5      │     │  W7      │       │
│   │  Poller  │────▶│  Matcher │────▶│  Drafter │────▶│  SMS     │       │
│   │  Agent   │     │  Engine  │     │  (4 var) │     │  Format  │       │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘       │
│        │                │                │                │              │
│        ▼                ▼                ▼                ▼              │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │                        tweets.db (W1)                         │      │
│   │  monitored_accounts │ tweets │ correlations │ drafts │ our   │      │
│   └──────────────────────────────────────────────────────────────┘      │
│        │                                              ▲                  │
│        │         ┌──────────┐     ┌──────────┐       │                  │
│        │         │  W8      │     │  W9      │       │                  │
│        │         │  Approval│────▶│  Poster  │───────┘                  │
│        │         │  Handler │     │          │                          │
│        │         └──────────┘     └──────────┘                          │
│        │              ▲                │                                 │
│        │              │                ▼                                 │
│        │         ┌─────────┐     ┌──────────┐                           │
│        │         │ V's SMS │     │  W11     │                           │
│        │         │ Response│     │  Voice   │                           │
│        │         └─────────┘     │  Learner │                           │
│        │                         └──────────┘                           │
│        │                              ▲                                  │
│        │                              │                                  │
│        │    ┌──────────┐    ┌──────────────────┐                        │
│        └───▶│  W2      │    │  W10 Archive     │                        │
│             │  X API   │    │  Ingester        │                        │
│             └──────────┘    └──────────────────┘                        │
│                                    ▲                                     │
│                                    │                                     │
│                            V's X Archive (when ready)                   │
│                                                                          │
│   Config: W4 Voice Variants │ W12 Pipeline Orchestrator                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Workers Overview

| ID | Component | Dependencies | Parallel Group | Est. Hours |
|----|-----------|--------------|----------------|------------|
| W1 | Database Schema | — | A | 0.75 |
| W2 | X API Wrapper | — | A | 1.5 |
| W3 | Position Matcher | — | A | 1.5 |
| W4 | Voice Variants | — | A | 1.0 |
| W5 | Draft Generator | W3, W4 | B | 2.0 |
| W6 | Polling Agent | W1, W2 | B | 1.5 |
| W7 | SMS Formatter | W5 | C | 1.0 |
| W8 | Approval Handler | W7 | C | 1.5 |
| W9 | Tweet Poster | W2, W8 | D | 0.75 |
| W10 | Archive Ingester | W1 | E (async) | 1.0 |
| W11 | Voice Learner | W9, W10 | F | 1.5 |
| W12 | Orchestrator | W6-W9 | G | 1.0 |

**Total Estimated**: ~14 hours

---

## Execution Waves

### Wave A (Parallel — Start Immediately)
**Workers**: W1, W2, W3, W4
**Dependencies**: None
**Can spawn**: 4 parallel threads immediately

```
W1 ─┬─ Database Schema
W2 ─┤─ X API Wrapper  
W3 ─┤─ Position Matcher      ──▶ All in parallel
W4 ─┴─ Voice Variants
```

### Wave B (After Wave A)
**Workers**: W5, W6
**Dependencies**: 
- W5 needs W3 + W4
- W6 needs W1 + W2

```
W5 ─── Draft Generator (needs W3, W4)
W6 ─── Polling Agent (needs W1, W2)
```

### Wave C (After Wave B)
**Workers**: W7, W8
**Dependencies**: W7 needs W5, W8 needs W7

```
W7 ─── SMS Formatter (needs W5)
W8 ─── Approval Handler (needs W7)
```

### Wave D (After Wave C)
**Workers**: W9
**Dependencies**: W2, W8

```
W9 ─── Tweet Poster (needs W2, W8)
```

### Wave E (Async — When Archive Arrives)
**Workers**: W10
**Dependencies**: W1, V's archive file

```
W10 ─── Archive Ingester (triggered when archive arrives)
```

### Wave F (After W9 + W10)
**Workers**: W11
**Dependencies**: W9, W10

```
W11 ─── Voice Learner (needs posted tweets + archive)
```

### Wave G (After D, E, F)
**Workers**: W12
**Dependencies**: W6, W7, W8, W9

```
W12 ─── Pipeline Orchestrator (final integration)
```

---

## Spawn Commands

### Wave A (Immediate)

```bash
# W1: Database Schema
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker-id W1 \
  --assignment-file N5/builds/x-thought-leader/workers/W1_database_schema.md

# W2: X API Wrapper
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker-id W2 \
  --assignment-file N5/builds/x-thought-leader/workers/W2_x_api_wrapper.md

# W3: Position Matcher
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker-id W3 \
  --assignment-file N5/builds/x-thought-leader/workers/W3_position_matcher.md

# W4: Voice Variants
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker-id W4 \
  --assignment-file N5/builds/x-thought-leader/workers/W4_voice_variants.md
```

---

## File Structure (Target)

```
Projects/x-thought-leader/
├── db/
│   ├── tweets.db
│   └── schema.sql
├── src/
│   ├── x_api.py
│   ├── position_matcher.py
│   ├── draft_generator.py
│   ├── sms_formatter.py
│   ├── approval_handler.py
│   ├── poster.py
│   ├── voice_learner.py
│   └── orchestrator.py
├── agents/
│   ├── poller.py
│   ├── main_pipeline.py
│   └── digest.py
├── config/
│   ├── voice_variants.yaml
│   ├── voice_examples.md
│   └── voice_model.yaml
├── docs/
│   └── README.md
└── build_plan.json
```

---

## Key Specifications

### Voice Variants
1. **SUPPORTIVE** 👍 — Builds on point, warm, collaborative
2. **CHALLENGING** 🤔 — Questions assumptions, curious
3. **SPICY** 🌶️ — Bold, contrarian, provocative
4. **COMEDIC** 😂 — Witty, playful, absurdist

### SMS Approval Format
```
🐦 @asanwal just tweeted:
"AI is going to change how we assess candidates"

Your drafts:

1️⃣ SUPPORTIVE:
Been saying this for years...

2️⃣ CHALLENGING:
True, but I'd push back...

3️⃣ SPICY:
Hot take: AI won't fix hiring...

4️⃣ COMEDIC:
Resumes watching AI enter the chat: 👀💀

Reply 1-4 to post, keyword+suggestion to refine, or "skip"
Expires: 11:59 PM ET
```

### Response Parsing
- `2` → Post variant 2
- `skip` or `0` → Skip this tweet
- `3 but shorter` → Refine variant 3 with suggestion

### Scheduling
- Polling: Every 15 min, 8 AM - 10 PM ET
- Daily digest: 10 PM ET
- Voice learning: Weekly, Sunday 11 PM ET

---

## Handoff Options

V can choose to:

1. **Spawn to parallel Zo threads** — Use spawn_worker.py to kick off Wave A immediately
2. **Hand off to Claude Code** — Export this plan + worker specs for external build
3. **Sequential in this thread** — Build each worker one at a time here

---

## Next Steps

1. **Confirm this plan** — Any adjustments needed?
2. **Get @asanwal's user ID** — Need to verify API keys work
3. **Spawn Wave A** — 4 parallel workers start building
4. **Monitor progress** — Use build orchestrator status commands

---

*Generated: 2026-01-09 02:50 AM ET*
*Orchestrator Thread: con_S4D4PEMvW09h9VCl*

