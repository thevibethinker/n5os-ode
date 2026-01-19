---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_ZoExvV6qS0wQiaYa
type: aar
build_slug: build-lesson-ledger
---

# After-Action Report: Build Lesson Ledger System

**Date:** 2026-01-19  
**Conversation:** con_ZoExvV6qS0wQiaYa  
**Build Slug:** build-lesson-ledger  
**Duration:** ~45 minutes  
**Outcome:** ✅ Complete

---

## What We Built

A **Build Lesson Ledger** system that enables real-time cross-worker communication during parallel builds. When multiple workers execute simultaneously, insights discovered by Worker 1 can now propagate to Workers 2 and 3 without requiring V to manually copy-paste context.

### Problem Solved

V observed that when launching 3 workers in parallel, clarifications or insights shared with one worker didn't automatically reach the others. This created friction (manual copy-paste) and risk (workers making inconsistent decisions).

### Deliverables

| Component | Path | Purpose |
|-----------|------|---------|
| Script | `N5/scripts/build_lesson_ledger.py` | CLI with init/read/append commands |
| Criteria Doc | `N5/prefs/operations/build-lesson-criteria.md` | Frame of reference for what qualifies as a lesson |
| init_build.py | Updated | Creates `BUILD_LESSONS.json` on every new build |
| Worker Template | Updated | Ledger instructions for workers |
| BUILD_template.md | Updated | Ledger reference for orchestrators |
| Operator Persona | Updated | Ledger-read step in orchestrator check-in |
| Rule | `fd9d280d` | Worker ledger discipline enforcement |

---

## How It Works

1. **On build init:** `BUILD_LESSONS.json` created automatically in build workspace
2. **Workers at start:** Read ledger for cross-cutting context from previous workers or V
3. **Workers during work:** Append lessons when they discover something others should know
4. **Orchestrator at wave boundary:** Reads ledger + completions, incorporates lessons into remaining briefs

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| JSON format (not Markdown) | V's preference — ledger is primarily AI-read, keep lightweight |
| Add rule upfront | V's instinct that instructions alone wouldn't ensure compliance |
| Single-worker build | Work was tightly coupled (script → init_build → template → persona), not parallelizable |
| Replace "Learnings Log" | Debugger QA found redundant manual section; ledger supersedes it |

---

## Lessons Learned

### What Worked Well

1. **Debugger QA pass was valuable** — caught 5 integration gaps that would have caused confusion
2. **Single-worker decision was correct** — the tight integration meant parallelization would have created coordination overhead
3. **V's instinct on rule was right** — brief instructions alone are too easy to skip

### What Could Improve

1. **SESSION_STATE was initialized late** — conversation started without state, had to create mid-stream. The init rule needs stronger enforcement.
2. **Plan had stale references** — changed format decision (MD → JSON) but didn't update all plan references. Need to update plan when design decisions change.

### Patterns Worth Reusing

- **QA pass after initial build** — Debugger review before calling it "done" catches real issues
- **Rule + brief instructions** — belt-and-suspenders approach for AI compliance
- **Frame of reference docs** — defining "what qualifies" prevents scope creep

---

## System Documentation

The Build Orchestrator System doc (`Documents/System/Build-Orchestrator-System.md`) needs to be updated to include the Build Lesson Ledger. This was flagged but deferred to conversation-end documentation flow.

---

## Commits

```
f42c52b4 feat(builds): Add build lesson ledger for cross-worker communication
4a5c7c8c fix(builds): Integration fixes from Debugger QA for lesson ledger
```

---

## Follow-Up Items

- [ ] Update `Documents/System/Build-Orchestrator-System.md` to document ledger (deferred to separate thread)
- [ ] Monitor worker compliance with ledger discipline over next few builds
- [ ] Consider adding conversation-end auto-extraction of lessons (supplementary, not primary)
