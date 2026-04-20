---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: n5os-ode
---

# Architect Workflow

## Overview

Planning and design workflow for major builds. The Architect produces a PLAN.md before implementation begins. This is mandatory for multi-file builds, novel architecture, or work exceeding ~50 lines of new code.

---

## Phase 1: Scope & Intent Clarification

Before designing anything:

1. **What is being built?** — Core deliverable in one sentence.
2. **Why does it need to exist?** — Problem it solves, gap it fills.
3. **What does success look like?** — Observable criteria (not vibes).
4. **What already exists?** — Scan workspace for related files, existing patterns, prior art.
5. **What are the constraints?** — Time, dependencies, compatibility, risk tolerance.

If any of these are unclear, ask before proceeding.

---

## Phase 2: Build Initialization

For tracked builds:

```bash
python3 N5/scripts/init_build.py <slug>
```

This creates the build scaffold at `N5/builds/<slug>/` with:
- `meta.json` — Build metadata, status, timestamps
- `drops/` — Task units (Drops) for parallel execution
- `deposits/` — Output artifacts from completed Drops
- `artifacts/` — Final deliverables

---

## Phase 3: PLAN.md Creation

Every major build gets a `PLAN.md` in the build directory.

### PLAN.md Template

```markdown
# Build Plan: [Title]

## Objective
[One paragraph: what we're building and why]

## Success Criteria
- [ ] [Observable outcome 1]
- [ ] [Observable outcome 2]
- [ ] [Observable outcome 3]

## Dependencies
- [File/system/service that must exist or be accessible]
- [External API, data source, or tool required]

## Phases

### Phase 1: [Name]
- **Deliverable**: [What this phase produces]
- **Tasks**:
  - [ ] [Specific task]
  - [ ] [Specific task]

### Phase 2: [Name]
- **Deliverable**: [What this phase produces]
- **Tasks**:
  - [ ] [Specific task]
  - [ ] [Specific task]

## Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk] | Low/Med/High | Low/Med/High | [Strategy] |

## Architecture Notes
[Diagrams, data flow, component relationships — as needed]

## Estimated Effort
[T-shirt size: S/M/L/XL with brief rationale]
```

---

## Phase 4: Nemawashi (Consensus Building)

Before implementation begins:

1. **Present the plan** — Share PLAN.md with the user.
2. **Surface tradeoffs** — Explicitly state what was considered and rejected, and why.
3. **Invite dissent** — "What am I missing?" is better than "Does this look good?"
4. **Get explicit approval** — Do not proceed to Builder without a clear go-ahead.

For small/obvious builds, nemawashi can be a single confirmation. For large builds, it may require iteration on the plan.

---

## Phase 5: Handoff to Builder

After plan approval:

1. Set the build status to `planned` in `meta.json`.
2. Route to Builder with a clear handoff:
   - Link to PLAN.md
   - Highlight any non-obvious decisions or constraints
   - Specify which phase to start with
3. Return to Operator after handoff.

---

## Parallelization Assessment

During planning, assess whether the build is parallelizable:

- **>5 independent task units** → Recommend Pulse orchestration
- **Tasks share no state** → Strong candidate for parallel Drops
- **Sequential dependencies exist** → Plan phases with dependency gates

Document parallelization decisions in PLAN.md under Architecture Notes.

---

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Skipping straight to code | Always produce PLAN.md first for major work |
| Vague success criteria | Must be observable and testable |
| Missing dependency check | Scan workspace before planning |
| Over-planning small work | Single-file, well-understood patterns skip to Builder |
| No risk assessment | Even "low risk" should be stated explicitly |

---

## References

- Build orchestration: `N5/scripts/init_build.py`
- Architectural principles: `Knowledge/architectural/principles.md`
- Planning prompt: `N5/prefs/operations/planning_prompt.md`
