---
created: 2026-01-24
last_edited: 2026-01-24
version: 2.0
provenance: con_plquQK5mpVEUO74p
---

# Build Plan: Prompt-to-Skill Conversion System (v2)

## Open Questions

All resolved. ✓

## Objective

Convert `Close Conversation.prompt.md` into **three focused skills** with shared logic in `N5/lib/close/` (SSOT) and built-in fail-safes.

**Deliverables:**
1. `Skills/prompt-to-skill/` — The conversion process (reusable)
2. `Skills/thread-close/` — Normal interactive threads
3. `Skills/drop-close/` — Pulse worker deposits
4. `Skills/build-close/` — Post-build synthesis
5. `N5/lib/close/` — Shared library (SSOT)

---

## Architecture

### Three Skills, One Library

```
N5/lib/close/                    # SSOT - authoritative shared code
├── __init__.py
├── core.py                      # Tier routing, main logic
├── emoji.py                     # 3-slot emoji system
├── positions.py                 # Position extraction
├── content_library.py           # Content library candidates
├── aar.py                       # AAR generation
├── guards.py                    # Fail-safe validators (NEW)
└── templates/
    └── aar.md.template

Skills/thread-close/             # Full interactive close
├── SKILL.md
└── scripts/
    └── close.py                 # Thin wrapper → N5/lib/close

Skills/drop-close/               # Pulse worker deposits
├── SKILL.md
└── scripts/
    └── close.py                 # Thin wrapper → N5/lib/close

Skills/build-close/              # Post-build synthesis
├── SKILL.md
└── scripts/
    └── close.py                 # Thin wrapper → N5/lib/close
```

### Fail-Safe Guards

Each skill wrapper validates context before executing:

```python
# Skills/thread-close/scripts/close.py
from N5.lib.close import guards, core

def main():
    state = guards.load_session_state(convo_id)
    
    # FAIL-SAFE: Detect wrong skill
    if state.get('drop_id'):
        guards.warn_wrong_skill(
            called="thread-close",
            suggested="drop-close",
            reason="SESSION_STATE has drop_id"
        )
        return 1
    
    if state.get('build_slug') and '--build' not in sys.argv:
        guards.warn_wrong_skill(
            called="thread-close", 
            suggested="build-close",
            reason="Build context detected"
        )
        return 1
    
    # Proceed with correct skill
    return core.run_thread_close(convo_id, tier=args.tier)
```

### Guard Behaviors

| Context Detected | Called Skill | Behavior |
|------------------|--------------|----------|
| `drop_id` in SESSION_STATE | thread-close | ⚠️ Suggest drop-close, exit |
| `drop_id` in SESSION_STATE | build-close | ⚠️ Suggest drop-close, exit |
| `build_slug` without drop | thread-close | ⚠️ Suggest build-close, exit |
| Normal thread | drop-close | ⚠️ Suggest thread-close, exit |
| Normal thread | build-close | ⚠️ Suggest thread-close, exit |
| Build complete | drop-close | ⚠️ Suggest build-close, exit |

---

## Checklist

### Stream 1: Foundation (Parallel)
- [ ] D1.1: Create `prompt-to-skill` skill
- [ ] D1.2: Create `N5/lib/close/` shared library
- [ ] D1.3: Build missing N5 scripts (`update_build.py`, `build_worker_complete.py`)

### Stream 2: Skills (Parallel, depends on Stream 1)
- [ ] D2.1: Create `thread-close` skill
- [ ] D2.2: Create `drop-close` skill  
- [ ] D2.3: Create `build-close` skill

### Stream 3: Finalize (Sequential, depends on Stream 2)
- [ ] D3.1: Integration tests + expunge original prompt

---

## Phase 1: Foundation

### D1.1: prompt-to-skill Skill

**Mission:** Create the reusable conversion process.

**Files:**
```
Skills/prompt-to-skill/
├── SKILL.md
├── scripts/
│   ├── assess.py          # Score prompt for skill eligibility
│   └── scaffold.py        # Generate skill folder structure
└── assets/
    └── skill-template/
        └── SKILL.md.template
```

**Success Criteria:**
- `python3 Skills/prompt-to-skill/scripts/assess.py "Prompts/X.prompt.md"` returns score
- `python3 Skills/prompt-to-skill/scripts/scaffold.py my-skill` creates structure

---

### D1.2: N5/lib/close/ Shared Library

**Mission:** Create SSOT for all close logic. This is the heavy lift.

**Files:**
```
N5/lib/close/
├── __init__.py
├── core.py                # Main logic: tier routing, session state
├── emoji.py               # 3-slot emoji system, title generation
├── positions.py           # Position extraction from conversations
├── content_library.py     # Content library candidate detection
├── aar.py                 # AAR generation
├── guards.py              # Fail-safe context validators
├── pii.py                 # PII audit
└── templates/
    ├── tier1.md.template
    ├── tier3-aar.md.template
    └── build-aar.md.template
```

**Key modules:**

`guards.py`:
```python
def load_session_state(convo_id: str) -> dict
def detect_context(state: dict) -> str  # Returns: "thread" | "drop" | "build"
def warn_wrong_skill(called: str, suggested: str, reason: str) -> None
def validate_thread_context(state: dict) -> tuple[bool, str]
def validate_drop_context(state: dict) -> tuple[bool, str]
def validate_build_context(slug: str) -> tuple[bool, str]
```

`core.py`:
```python
def run_thread_close(convo_id: str, tier: int = None, dry_run: bool = False) -> int
def run_drop_close(convo_id: str, drop_id: str, build_slug: str) -> int
def run_build_close(slug: str, dry_run: bool = False) -> int
```

**Source:** Migrate logic from:
- `N5/scripts/conversation_end_router.py`
- `N5/scripts/conversation_end_quick.py`
- `N5/scripts/conversation_end_standard.py`
- `N5/scripts/conversation_end_full.py`
- `N5/scripts/conversation_pii_audit.py`
- `N5/config/emoji-legend.json`
- `N5/config/commit_targets.json`
- `N5/prefs/operations/conversation-end-v5.md`

**Success Criteria:**
- `from N5.lib.close import core, guards` works
- All functions importable and documented

---

### D1.3: Missing N5 Scripts

**Mission:** Create build-system utilities referenced by Close Conversation.

**Files:**
- `N5/scripts/update_build.py` — Build state management
- `N5/scripts/build_worker_complete.py` — Legacy worker notification

**Note:** These stay in N5/scripts (build-system, not close-specific).

**Success Criteria:**
- `python3 N5/scripts/update_build.py status <slug>` works
- `python3 N5/scripts/update_build.py complete <slug> <drop_id> --decisions '[...]'` works

---

## Phase 2: Skills

### D2.1: thread-close Skill

**Mission:** Create skill for normal interactive threads.

**Files:**
```
Skills/thread-close/
├── SKILL.md
└── scripts/
    └── close.py
```

**SKILL.md content:**
- When to use: Normal threads, manual orchestrators
- Quick start: `python3 Skills/thread-close/scripts/close.py --convo-id <id>`
- Tiers explained (1/2/3)
- What it does: SESSION_STATE check, tier routing, position extraction, AAR

**close.py** (~50 lines):
- Parse args (--convo-id, --tier, --dry-run)
- Load session state
- **Guard check:** If drop context → warn, suggest drop-close, exit
- **Guard check:** If build context → warn, suggest build-close, exit
- Call `core.run_thread_close()`
- Format output

---

### D2.2: drop-close Skill

**Mission:** Create skill for Pulse worker deposits.

**Files:**
```
Skills/drop-close/
├── SKILL.md
└── scripts/
    └── close.py
```

**SKILL.md content:**
- When to use: Pulse Drops (headless workers)
- Quick start: `python3 Skills/drop-close/scripts/close.py --convo-id <id>`
- What it does: Write structured deposit, NO commits, handoff to orchestrator
- Deposit format documented

**close.py** (~50 lines):
- Parse args (--convo-id)
- Load session state
- **Guard check:** If no drop_id → warn, suggest thread-close, exit
- Extract drop_id, build_slug from state
- Call `core.run_drop_close()`
- Write deposit JSON

---

### D2.3: build-close Skill

**Mission:** Create skill for post-build synthesis.

**Files:**
```
Skills/build-close/
├── SKILL.md
└── scripts/
    └── close.py
```

**SKILL.md content:**
- When to use: After Pulse build completes (via `pulse finalize`)
- Quick start: `python3 Skills/build-close/scripts/close.py --slug <build-slug>`
- What it does: Aggregate deposits, synthesize decisions, extract positions, generate build AAR

**close.py** (~60 lines):
- Parse args (--slug, --dry-run)
- **Guard check:** Build exists and is terminal
- **Guard check:** Not a single-drop scenario (suggest drop-close)
- Read all deposits from `N5/builds/<slug>/deposits/`
- Call `core.run_build_close()`
- Write BUILD_CLOSE.md, BUILD_AAR.md

---

## Phase 3: Finalize

### D3.1: Integration Tests + Expunge

**Mission:** Verify everything works, clean up old code.

**Tests:**
1. `thread-close --dry-run` on a test thread
2. `drop-close` with mock drop context
3. `build-close --dry-run` on a completed build
4. **Guard tests:** Call wrong skill, verify warning

**Expunge steps:**
1. `grep -r "Close Conversation" /home/workspace` — find references
2. `grep -r "conversation_end_" /home/workspace` — find old script refs
3. Archive: `mv "Prompts/Close Conversation.prompt.md" "Prompts/Archive/"`
4. Create redirect stub at original location
5. Delete old scripts from N5/scripts/ (after confirming no other refs)

**Success Criteria:**
- All three skills work in isolation
- Guards catch wrong invocations
- No dangling references to old prompt/scripts

---

## MECE Validation

| Scope Item | Owner | Must Not Touch |
|------------|-------|----------------|
| prompt-to-skill SKILL.md + scripts | D1.1 | N5/lib/close |
| N5/lib/close/* (all modules) | D1.2 | Skills/**/close.py |
| update_build.py, build_worker_complete.py | D1.3 | N5/lib/close |
| Skills/thread-close/* | D2.1 | drop-close, build-close |
| Skills/drop-close/* | D2.2 | thread-close, build-close |
| Skills/build-close/* | D2.3 | thread-close, drop-close |
| Testing + expunge | D3.1 | Creating new code |

✅ No overlaps. No gaps.

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Import path issues with N5/lib | Medium | Medium | Test imports early in D1.2 |
| Guards too aggressive (false positives) | Low | Medium | Include --force flag to bypass |
| Old scripts have hidden dependents | Medium | High | Grep thoroughly before delete |

---

## Estimated Effort

| Drop | Description | Complexity | Est. Time |
|------|-------------|------------|-----------|
| D1.1 | prompt-to-skill skill | Medium | 15 min |
| D1.2 | N5/lib/close/ library | **High** | 35 min |
| D1.3 | Missing N5 scripts | Medium | 15 min |
| D2.1 | thread-close skill | Low | 10 min |
| D2.2 | drop-close skill | Low | 10 min |
| D2.3 | build-close skill | Low | 10 min |
| D3.1 | Tests + expunge | Medium | 15 min |

**Total:** ~110 min Zo execution time

---

## Execution Mode

**Pulse with auto-spawn:**
- Stream 1: D1.1, D1.2, D1.3 in parallel
- Stream 2: D2.1, D2.2, D2.3 in parallel (all depend on D1.2)
- Stream 3: D3.1 sequential (depends on all of Stream 2)
