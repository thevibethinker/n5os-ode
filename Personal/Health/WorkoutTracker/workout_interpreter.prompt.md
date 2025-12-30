---
created: 2025-12-29
last_edited: 2025-12-29
version: 1.0
provenance: con_wQnAwnoiB1GeFvSF
tool: false
---

# Workout Interpreter Contract

> **Purpose:** Defines how Zo interprets V's natural language workout reports against baseline protocols.

---

## Context Loading

Before interpreting any workout report, ensure you have loaded:
- `file 'Personal/Health/COACHING_NOTES.md'` → Contains **Active Training Protocols** section with baseline exercises

---

## Interpretation Process

### Step 1: Identify Session Type

Map V's description to one of:
- `upper` — Upper-biased circuit
- `lower` — Lower-biased circuit  
- `core` — Core-focused work
- `full_body` — Mixed or complete workout
- `mobility` — Stretching, foam rolling, recovery

**Signals:**
- "upper circuit" / "push-ups and rows" → `upper`
- "lower circuit" / "squats and bridges" → `lower`
- "just core" / "abs" → `core`
- "full thing" / "everything" → `full_body`
- "stretching" / "foam rolled" → `mobility`

### Step 2: Compare Against Baseline

Load the baseline protocol for the identified session type from COACHING_NOTES.md.

For each exercise in the baseline:
1. **Completed as prescribed** → Include in exercises list with baseline sets/reps
2. **Modified** → Note what changed (different reps, different variation)
3. **Skipped** → Note as skipped with reason if given
4. **Substituted** → Note original and substitute

For exercises NOT in baseline:
- **Added** → Include with sets/reps as described

### Step 3: Extract Metadata

From V's description, extract:
- **RPE** (1-10): Look for "RPE X", "felt like a X", "easy" (3-4), "moderate" (5-6), "hard" (7-8)
- **Duration**: Look for "X minutes", "took about X min"
- **Felt before**: "felt good going in", "was tired", "stiff"
- **Felt after**: "felt easy", "was gassed", "could do more"
- **Context**: Any situational notes (back was tight, got interrupted, etc.)

---

## Confirmation Format

**Always show this before logging:**

```
📝 Logging:
- Session: {session_type} ({phase})
- Completed: {exercise} ({sets}×{reps}), ...
- Skipped: {exercise} ({reason}) [if any]
- Added: {exercise} ({sets}×{reps}) [if any]
- Modified: {exercise} → {what changed} [if any]
- RPE: {rpe}/10
- Duration: {duration} min [if mentioned]
- Notes: {context}

Confirm? (y / correct me)
```

**Wait for V to confirm before logging.** If V corrects, update interpretation and re-confirm.

---

## Logging Command

After confirmation, execute:

```bash
python3 Personal/Health/WorkoutTracker/log_strength.py log \
  --type {session_type} \
  --rpe {rpe} \
  --duration {duration} \
  --phase {current_phase} \
  --exercises-json '{exercises_array}' \
  --deviation-notes "{deviations}" \
  --felt-before "{felt_before}" \
  --felt-after "{felt_after}" \
  --notes "{context}"
```

### Exercises JSON Format

```json
[
  {"exercise": "push_ups", "sets": 1, "reps": 8, "notes": "standard"},
  {"exercise": "dead_bugs", "sets": 1, "reps": 8, "notes": "per side"},
  {"exercise": "bent_over_rows", "sets": 0, "reps": 0, "notes": "SKIPPED - back tight"}
]
```

Use `sets: 0, reps: 0` for skipped exercises to preserve the record that they were in the baseline but not performed.

---

## Edge Cases

### Partial Completion
> "Only got through 3 exercises before a call"

- Log what was completed
- Note remaining as skipped with reason "interrupted"
- Add context note about interruption

### Substitutions
> "Did wall push-ups instead of standard"

- Log as `{"exercise": "wall_push_ups", "sets": 1, "reps": 8, "notes": "substituted for standard push-ups"}`
- Deviation note: "substituted wall push-ups for standard"

### Extra Work
> "Plus an extra set of push-ups"

- Add entry: `{"exercise": "push_ups", "sets": 1, "reps": 8, "notes": "extra set"}`
- Or increment sets on original entry if same exercise

### Modified Reps/Sets
> "Did 12 push-ups instead of 8"

- Log actual reps performed
- Note modification: `"notes": "12 instead of baseline 8"`

### No Deviations
> "Did the full upper circuit as prescribed"

- Log all baseline exercises with standard sets/reps
- No deviation notes needed
- Simple confirmation

---

## Current Phase Reference

Check COACHING_NOTES.md for current phase:
- `ramp_week1` — Week 1 ramp-up (RPE target 5/10)
- `ramp_week2` — Week 2 ramp-up (RPE target 6/10)
- `phase1` — Full Jair Phase 1

---

## Example Interpretations

**Input:** "Did upper circuit, skipped rows because my back was weird, added an extra set of push-ups. Felt pretty easy, maybe RPE 4."

**Output:**
```
📝 Logging:
- Session: upper (ramp_week1)
- Completed: push_ups (2×8), dead_bugs (1×8/side), bird_dogs (1×6/side), pull_aparts (1×12)
- Skipped: bent_over_rows (back discomfort)
- Added: push_ups (+1 set)
- RPE: 4/10
- Notes: Back felt off

Confirm? (y / correct me)
```

**Input:** "Just did 10 minutes of core work, dead bugs and bird dogs"

**Output:**
```
📝 Logging:
- Session: core (ramp_week1)
- Completed: dead_bugs (1×8/side), bird_dogs (1×6/side)
- RPE: ?/10 (not specified)
- Duration: 10 min

Confirm? (y / correct me)
```

