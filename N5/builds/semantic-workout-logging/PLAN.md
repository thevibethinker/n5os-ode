---
created: 2025-12-29
last_edited: 2025-12-29
version: 1.0
type: build_plan
status: ready
---

# Plan: Semantic Workout Logging for Vibe Trainer

**Objective:** Enable V to report workouts in natural language; Zo interprets against baseline protocols, confirms interpretation, and logs structured data.

**Trigger:** V wants flexibility to describe deviations from standard protocols ("did X but skipped Y, added Z") without rigid formats.

**Key Design Principle:** Plans are FOR AI execution. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved during planning -->
- [x] Where do baseline protocols live? → `Personal/Health/COACHING_NOTES.md` (already added)
- [x] Database schema? → `strength_sessions` table already created in `workouts.db`
- [x] How does Zo know to load protocols? → Vibe Trainer persona loads `COACHING_NOTES.md` at session start

---

## Checklist

### Phase 1: Logging Infrastructure
- ☑ Update `log_strength.py` to accept JSON exercises payload cleanly
- ☑ Add `--exercises-json` flag for structured logging
- ☑ Add `--deviation-notes` flag for capturing what differed from baseline
- ☑ Test: Log a session with exercises JSON and verify DB storage

### Phase 2: Semantic Interpreter Prompt
- ☑ Create `workout_interpreter.prompt.md` that defines the interpretation contract
- ☑ Document the confirmation format (what Zo shows V before logging)
- ☑ Add prompt to Vibe Trainer persona's auto-load context (ref in COACHING_NOTES.md)
- ☑ Test: Simulate natural language input → structured output (contract documented)

### Phase 3: End-to-End Validation
- ☐ Run full flow: V reports → Zo interprets → V confirms → Zo logs [READY FOR LIVE TEST]
- ☐ Verify DB entry matches interpretation
- ☐ Test edge cases: partial completion, substitutions, extras

---

## Phase 1: Logging Infrastructure

### Affected Files
- `Personal/Health/WorkoutTracker/log_strength.py` - UPDATE - Add exercises JSON support and deviation notes
- `Personal/Health/workouts.db` - VERIFY - Confirm schema supports exercises_json field

### Changes

**1.1 Enhance `log_strength.py`:**

Add `--exercises-json` argument that accepts a JSON string of exercises performed:
```json
[
  {"exercise": "push_ups", "sets": 1, "reps": 8, "notes": "standard"},
  {"exercise": "dead_bugs", "sets": 1, "reps": 8, "notes": "per side"}
]
```

Add `--deviation-notes` argument for free-text explanation of what differed from baseline.

**1.2 Update `log` subcommand:**

Current: `log --type X --rpe Y --duration Z --notes "..."`

New: `log --type X --rpe Y --duration Z --exercises-json '[...]' --deviation-notes "skipped rows" --felt-before "good" --felt-after "easy"`

### Unit Tests
- `python3 log_strength.py log --type upper --rpe 5 --exercises-json '[{"exercise":"push_ups","sets":1,"reps":8}]'` → Success, verify DB has exercises_json populated
- `python3 log_strength.py recent` → Shows logged session with exercise details

---

## Phase 2: Semantic Interpreter Prompt

### Affected Files
- `Personal/Health/WorkoutTracker/workout_interpreter.prompt.md` - CREATE - Interpretation contract for semantic parsing
- `Personal/Health/COACHING_NOTES.md` - UPDATE - Add reference to interpreter prompt

### Changes

**2.1 Create interpretation contract prompt:**

The prompt defines:
1. How to parse natural language workout reports against baseline protocols
2. The confirmation format shown to V before logging
3. How to handle deviations (skipped, added, modified, substituted)
4. Edge cases (partial completion, interruptions, modified reps/sets)

**2.2 Confirmation format specification:**

```
📝 Logging:
- Session: {session_type} ({phase})
- Completed: {exercise} ({sets}×{reps}), ...
- Skipped: {exercise} ({reason})
- Added: {exercise} ({sets}×{reps})
- Modified: {exercise} ({what changed})
- RPE: {rpe}/10
- Duration: {duration} min
- Notes: {context}

Confirm? (y/correct me)
```

### Unit Tests
- Input: "Did upper circuit, skipped rows, RPE 5" → Output shows 4/5 exercises, rows marked skipped
- Input: "Upper circuit plus extra push-ups, felt easy" → Output shows standard + 1 extra set push-ups

---

## Phase 3: End-to-End Validation

### Affected Files
- No new files - validation only

### Changes

**3.1 Full flow test:**
1. V says: "Did upper circuit, skipped rows because back was tight, added an extra set of push-ups. RPE 4."
2. Zo interprets and shows confirmation
3. V confirms
4. Zo runs: `python3 log_strength.py log --type upper --rpe 4 --exercises-json '[...]' --deviation-notes "skipped rows (back tight), added extra push-up set"`
5. Verify: `python3 log_strength.py recent` shows correct entry

**3.2 Edge case tests:**
- Partial completion: "Only got through 3 exercises before a call"
- Substitution: "Did wall push-ups instead of standard"
- Different reps: "Did 12 push-ups instead of 8"
- No deviations: "Did the full upper circuit as prescribed"

### Unit Tests
- DB query shows correct exercises_json structure
- Deviation notes captured accurately
- Session type matches what was reported

---

## Success Criteria

1. V can report workouts in natural language without following any specific format
2. Zo correctly interprets reports against baseline protocols in COACHING_NOTES.md
3. Zo shows clear confirmation before logging (no silent writes)
4. Database captures: exercises performed, deviations, RPE, duration, context
5. `log_strength.py recent` displays logged sessions with full detail

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Zo misinterprets V's report | Always show confirmation before logging; V can correct |
| Baseline protocols not loaded | Vibe Trainer persona explicitly loads COACHING_NOTES.md |
| Schema drift (exercises_json format) | Define canonical format in interpreter prompt |
| V forgets to confirm | Zo waits for explicit confirmation; no auto-log |

---

## Nemawashi (Alternatives Considered)

### Option A: Pure LLM Semantic Interpretation ✅ SELECTED
- **Pros:** Maximum flexibility, no rigid format, V asked for this explicitly
- **Cons:** Requires me to always load protocols
- **Why selected:** Matches V's stated preference for natural language flexibility

### Option B: Structured Template + LLM
- **Pros:** More predictable, forced field completion
- **Cons:** Adds friction, loses natural feel
- **Why rejected:** V explicitly said no rigid regex/format

### Option C: Dedicated CLI with Fuzzy Matching
- **Pros:** Deterministic, V could log without Zo
- **Cons:** Loses semantic flexibility entirely
- **Why rejected:** Defeats the purpose of V's request

---

## Level Upper Review

*Skipped for this build — straightforward scope, low complexity, no trap doors identified.*

---

## Handoff to Builder

**Plan Status:** Ready for execution

**Starting Phase:** Phase 1

**Context:** 
- Database table `strength_sessions` already exists
- Basic `log_strength.py` already created (needs enhancement)
- Baseline protocols already in `COACHING_NOTES.md`

**Builder Instructions:**
1. Execute Phase 1: Enhance log_strength.py
2. Execute Phase 2: Create interpreter prompt
3. Execute Phase 3: Validate end-to-end
4. Update checklist as each item completes
5. Return to Operator when done




