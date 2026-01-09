---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_S4D4PEMvW09h9VCl
---

# Build: X Thought Leadership Engine

## Status: Ready to Spawn

| Metric | Value |
|--------|-------|
| Total Workers | 12 |
| Ready (no deps) | 4 |
| Estimated Hours | 11.5 |
| Project Dir | `Projects/x-thought-leader/` |

## Dependency Graph

```
PHASE 1 (Parallel - No Dependencies)
┌─────────────────────────────────────────────────────────────────┐
│  W1 Database    W2 X API    W3 Matcher    W4 Voice Config      │
│     (0.5h)       (1h)         (1h)           (0.75h)           │
└─────────────────────────────────────────────────────────────────┘
         │           │            │               │
         ▼           ▼            ▼               ▼
PHASE 2 (Dependencies Satisfied)
┌─────────────────────────────────────────────────────────────────┐
│  W6 Poller ◄── W1+W2                                           │
│     (1h)                                                        │
│                                                                 │
│  W5 Draft Generator ◄── W3+W4                                  │
│     (1.5h)                                                      │
│                                                                 │
│  W10 Archive Ingester ◄── W1                                   │
│     (1h)                                                        │
└─────────────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
PHASE 3
┌─────────────────────────────────────────────────────────────────┐
│  W7 SMS Interface ◄── W5                                       │
│     (1.5h)                                                      │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
PHASE 4
┌─────────────────────────────────────────────────────────────────┐
│  W8 Poster ◄── W2+W7         W9 Orchestrator ◄── W6+W5+W7     │
│     (0.75h)                       (1h)                          │
└─────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
PHASE 5
┌─────────────────────────────────────────────────────────────────┐
│  W11 Voice Learner ◄── W8+W4                                   │
│     (1.5h)                                                      │
│                                                                 │
│  W12 Prompt Interface ◄── W9                                   │
│     (0.5h)                                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Workers

| ID | Component | Status | Deps | Hours | Spec |
|----|-----------|--------|------|-------|------|
| W1 | Database Schema | 🟡 Ready | - | 0.5 | `workers/W1_database_schema.md` |
| W2 | X API Wrapper | 🟡 Ready | - | 1.0 | `workers/W2_x_api_wrapper.md` |
| W3 | Position Matcher | 🟡 Ready | - | 1.0 | `workers/W3_position_matcher.md` |
| W4 | Voice Config | 🟡 Ready | - | 0.75 | `workers/W4_voice_variants.md` |
| W5 | Draft Generator | ⏳ Blocked | W3,W4 | 1.5 | `workers/W5_draft_generator.md` |
| W6 | Polling Agent | ⏳ Blocked | W1,W2 | 1.0 | `workers/W6_poller_agent.md` |
| W7 | SMS Interface | ⏳ Blocked | W5 | 1.5 | `workers/W7_sms_formatter.md` |
| W8 | Poster | ⏳ Blocked | W2,W7 | 0.75 | `workers/W8_approval_handler.md` |
| W9 | Orchestrator | ⏳ Blocked | W6,W5,W7 | 1.0 | `workers/W9_poster.md` |
| W10 | Archive Ingester | ⏳ Blocked | W1 | 1.0 | `workers/W10_archive_ingester.md` |
| W11 | Voice Learner | ⏳ Blocked | W8,W4 | 1.5 | `workers/W11_voice_learner.md` |
| W12 | Prompt Interface | ⏳ Blocked | W9 | 0.5 | `workers/W12_orchestrator.md` |

## Spawn Commands

### Phase 1 (Run in Parallel)

```bash
# W1: Database Schema
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker W1 \
  --spec "N5/builds/x-thought-leader/workers/W1_database_schema.md"

# W2: X API Wrapper
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker W2 \
  --spec "N5/builds/x-thought-leader/workers/W2_x_api_wrapper.md"

# W3: Position Matcher
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker W3 \
  --spec "N5/builds/x-thought-leader/workers/W3_position_matcher.md"

# W4: Voice Config
python3 N5/scripts/spawn_worker.py \
  --project x-thought-leader \
  --worker W4 \
  --spec "N5/builds/x-thought-leader/workers/W4_voice_variants.md"
```

## Key Design Decisions

1. **SMS Approval**: V responds with 1-4 or "skip". Supports refinement ("3 but shorter")
2. **4 Variants**: Supportive, Challenging, Spicy, Comedic
3. **Replies Only**: Posts as replies to appear in target's mentions
4. **EOD Expiry**: Drafts expire at 11:59 PM ET same day
5. **Voice Learning**: Tracks selections to improve over time
6. **17 tweets/day limit**: Rate limit warning at 15/day

## Context Files

- Positions DB: `N5/data/positions.db` (105 positions)
- Voice transformer: `N5/scripts/voice_transformer.py`
- Social media voice: `N5/prefs/communication/social-media-voice.md`

---

*Orchestrator: con_S4D4PEMvW09h9VCl*

