---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_plan
status: draft
provenance: con_ZoExvV6qS0wQiaYa
---

# Plan: Build Lesson Ledger System

**Objective:** Create an append-only ledger for cross-worker communication that enables real-time propagation of insights during parallel builds.

**Trigger:** V observed that insights shared with Worker 1 don't propagate to concurrent Workers 2 and 3, requiring manual copy-paste. This system enables workers to share lessons as they're discovered.

**Key Design Principle:** The ledger must work without human intervention — workers should naturally recognize what qualifies as a lesson and append it without prompting.

---

## Open Questions

- [x] What should the file be called? → `BUILD_LESSONS.json` (V confirmed)
- [x] Should workers read at start or continuously? → Read at start (workers are atomic enough)
- [x] Should the ledger be included in worker brief template as a section, or as instructions? → Instructions (less overhead, flexible)
- [x] Do we need a rule for this, or are worker brief instructions sufficient? → Yes, add rule (V's instinct)

---

## Checklist

### Phase 1: Core Infrastructure
- ☑ Create `build_lesson_ledger.py` script with `init`, `read`, `append` commands
- ☑ Create frame of reference doc defining what constitutes a lesson
- ☑ Test script manually

### Phase 2: Integration
- ☑ Update `init_build.py` to create `BUILD_LESSONS.json` on build init
- ☑ Update worker brief template with ledger instructions
- ☑ Add rule for worker ledger discipline

### Phase 3: Validation
- ☑ Test end-to-end: init build → verify ledger created
- ☑ Test append/read cycle
- ☑ Commit with clear message

### Phase 4: Integration Fixes (from Debugger QA)
- ☑ Fix #1: Update BUILD_template.md to reference ledger instead of manual "Learnings Log"
- ☑ Fix #3: Update this PLAN.md to reflect JSON format (stale .md references)
- ☑ Fix #4: Add ledger-read step to orchestrator workflow in persona
- ☑ Fix #5: Update Operator persona with ledger-read instruction

---

## Phase 1: Core Infrastructure

### Affected Files
- `N5/scripts/build_lesson_ledger.py` - CREATE - Main script for ledger operations
- `N5/prefs/operations/build-lesson-criteria.md` - CREATE - Frame of reference for what qualifies as a lesson

### Changes

**1.1 Create `build_lesson_ledger.py`:**

Script with three commands:
- `init <slug>` — Create empty `BUILD_LESSONS.json` with header
- `read <slug> [--since timestamp]` — Display ledger contents (optionally filtered)
- `append <slug> "<message>" [--source W1.1|V|orchestrator]` — Add timestamped entry

Entry format:
```markdown
## 2026-01-19 09:45 | W1.1 | @all
The API returns snake_case, not camelCase. Adjust all parsers accordingly.
```

Fields:
- Timestamp (ISO-ish for human readability)
- Source (worker ID, "V", or "orchestrator")
- Audience tag (@all, @W2.*, @data-workers, etc. — start simple with @all)

**1.2 Create frame of reference doc:**

`N5/prefs/operations/build-lesson-criteria.md` defines:

**What qualifies as a lesson worth logging:**
1. Cross-cutting insights that apply to multiple workers (not just your scope)
2. Discovered constraints that contradict assumptions in the plan
3. API behavior, schema quirks, or data format surprises
4. Patterns or conventions that emerged and should be consistent
5. Things V said that should propagate to other workers
6. Mistakes made that others should avoid (anti-patterns discovered)
7. Decisions made that affect how other workers should proceed

**What does NOT belong:**
- Progress updates (that goes in completion reports)
- Questions for V (ask directly)
- Scope-specific details that don't affect others
- Blockers (those go in completion reports too)

**Trigger moments (when to ask yourself "should I log this?"):**
- V provides clarification during your work
- You discover something that surprises you
- You make a decision that another worker might make differently
- You finish a subtask and realize "I wish I'd known X earlier"

### Unit Tests
- `init`: Creates `N5/builds/<slug>/BUILD_LESSONS.json` with correct header
- `read`: Returns empty for fresh ledger, returns entries after append
- `append`: Adds properly formatted entry with timestamp
- Error handling: Graceful fail if build doesn't exist

---

## Phase 2: Integration

### Affected Files
- `N5/scripts/init_build.py` - UPDATE - Add ledger creation to build init
- `N5/templates/build/worker_brief_template.md` - UPDATE - Add ledger instructions section

### Changes

**2.1 Update `init_build.py`:**

After creating `BUILD.md`, `PLAN.md`, etc., also call ledger init:
```python
# Initialize lesson ledger
subprocess.run(["python3", str(WORKSPACE / "N5" / "scripts" / "build_lesson_ledger.py"), "init", slug], check=True)
```

Or inline the creation (simpler):
```python
# Create lesson ledger
ledger_content = f"""---
created: {today}
purpose: Cross-worker insights and lessons (append-only)
build_slug: {slug}
---

# Build Lesson Ledger

**Instructions:** 
- Read this file before starting your work
- Append lessons using: `python3 N5/scripts/build_lesson_ledger.py append {slug} "Your lesson" --source W#.#`

---

<!-- Entries appear below -->
"""
(build_dir / "BUILD_LESSONS.json").write_text(ledger_content)
```

Add `BUILD_LESSONS.json` to the printed output showing what was created.

**2.2 Update worker brief template:**

Add new section after "Context from Previous Waves":

```markdown
---

## Build Lesson Ledger

**Before starting your work:**
```bash
python3 N5/scripts/build_lesson_ledger.py read {{SLUG}}
```

**When you discover something other workers should know:**
```bash
python3 N5/scripts/build_lesson_ledger.py append {{SLUG}} "Your lesson here" --source W{{WAVE}}.{{SEQ}}
```

**What qualifies as a lesson?** Cross-cutting insights, discovered constraints, API surprises, patterns that should be consistent, things V said that should propagate. See `file 'N5/prefs/operations/build-lesson-criteria.md'` for full criteria.

---
```

Also update the "Report Back" section to remind workers:
```markdown
### Before You Finish
- [ ] Check: Did you learn anything that other workers should know?
- [ ] If yes: `python3 N5/scripts/build_lesson_ledger.py append {{SLUG}} "..." --source W{{WAVE}}.{{SEQ}}`
```

### Unit Tests
- After `init_build.py`: `BUILD_LESSONS.json` exists in build folder
- Worker brief template: Contains ledger section with correct placeholders

---

## Phase 3: Validation

### Affected Files
- No new files — testing existing changes

### Changes

**3.1 End-to-end test:**
```bash
# Create test build
python3 N5/scripts/init_build.py ledger-test --title "Ledger Test Build"

# Verify ledger exists
cat N5/builds/ledger-test/BUILD_LESSONS.json

# Test append
python3 N5/scripts/build_lesson_ledger.py append ledger-test "Test lesson from validation" --source V

# Verify entry
python3 N5/scripts/build_lesson_ledger.py read ledger-test

# Cleanup
rm -rf N5/builds/ledger-test
```

**3.2 Commit:**
```bash
git add N5/scripts/build_lesson_ledger.py
git add N5/prefs/operations/build-lesson-criteria.md
git add N5/scripts/init_build.py
git add N5/templates/build/worker_brief_template.md
git commit -m "feat(builds): Add build lesson ledger for cross-worker communication

- New script: build_lesson_ledger.py (init/read/append)
- New doc: build-lesson-criteria.md (frame of reference)
- Updated init_build.py to create BUILD_LESSONS.json
- Updated worker_brief_template.md with ledger instructions

Enables real-time propagation of insights across parallel workers."
```

### Unit Tests
- Ledger file created with build
- Append adds entry
- Read shows entries
- Worker brief template renders correctly

---

## Phase 4: Integration Fixes (from Debugger QA)

### Affected Files
- `N5/templates/build/BUILD_template.md` - UPDATE - Reference ledger instead of manual Learnings Log
- `N5/builds/build-lesson-ledger/PLAN.md` - UPDATE - Fix stale .md references to .json
- Operator persona (via `edit_persona`) - UPDATE - Add ledger-read to orchestrator workflow

### Changes

**4.1 Fix #1: Update BUILD_template.md**

Replace the manual "Learnings Log" section with ledger reference:
```markdown
## Build Lesson Ledger

**Read lessons from all workers:**
```bash
python3 N5/scripts/build_lesson_ledger.py read {{SLUG}}
```

Lessons are logged by workers in real-time to `BUILD_LESSONS.json`. Review after each wave completion and incorporate relevant insights into subsequent worker briefs.
```

**4.2 Fix #3: Update PLAN.md stale references**

Replace all `BUILD_LESSONS.json` references with `BUILD_LESSONS.json` in this plan file.

**4.3 Fix #4 & #5: Update Operator persona**

Add to the build orchestration section of Operator persona:
```
**After each wave completes:**
1. Read completions from `completions/`
2. Read lesson ledger: `python3 N5/scripts/build_lesson_ledger.py read <slug>`
3. Incorporate lessons into remaining worker briefs before launching next wave
```

### Unit Tests
- BUILD_template.md contains ledger reference section
- PLAN.md has no `.md` references for ledger (all `.json`)
- Operator persona includes ledger-read step

---

## Worker Briefs

**This is a single-worker build.** The work is tightly coupled integration — not parallelizable. 

Architect (me) will hand off to Builder for execution.

---

## Success Criteria

1. `init_build.py` creates `BUILD_LESSONS.json` in every new build
2. `build_lesson_ledger.py` successfully inits, reads, and appends
3. Worker brief template includes ledger instructions with correct placeholders
4. Frame of reference doc clearly defines what qualifies as a lesson
5. All tests pass
6. Committed to git

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Workers forget to read/write ledger | Clear instructions in brief + "Before You Finish" checklist |
| Ledger gets cluttered with non-lessons | Strong frame of reference doc with "What does NOT belong" |
| Script errors block worker progress | Graceful error handling, ledger is enhancement not blocker |

---

## Level Upper Review

**Skipping for this build.** This is tactical infrastructure work with clear requirements. No divergent thinking needed.

---

## Alternatives Considered (Nemawashi)

**Alternative 1: Rule-based approach**
- Add a rule that triggers in build contexts requiring ledger discipline
- Pro: More reliable AI behavior
- Con: Heavier, adds cognitive load to rule system
- Decision: Start with brief instructions, add rule later if compliance is poor

**Alternative 2: Structured JSON instead of Markdown**
- Machine-readable format
- Pro: Easier to parse programmatically
- Con: Harder to read/edit manually
- Decision: JSON — ledger is primarily AI-read, keep lightweight

**Alternative 3: Build into conversation-end workflow**
- Auto-extract lessons at end of worker conversation
- Pro: Happens automatically
- Con: Misses in-the-moment insights, timing too late
- Decision: Real-time append is the point; conversation-end is supplementary at best
