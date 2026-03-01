---
created: 2026-02-21
last_edited: 2026-02-21
version: 2.0
provenance: con_mG5yzbSSJUnMnZcK
---

# Dark Factory Elevation — Implementation Plan

## Objective

Elevate N5OS from Level 3→4 on the Shapiro framework by closing the validation gap. The system already excels at orchestration (Pulse), worker isolation (P38), and audit (P39). The missing piece: **spec quality and behavioral validation**.

After this work, builds should be assessable by their *scenario outcomes* rather than by reading their implementation.

## Guiding Constraint (adapted from StrongDM)

> "Specs must be complete enough that output quality can be assessed without reading the output's implementation."

This is the non-technical founder's version of "code must not be reviewed by humans."

---

## Phase 1: Scenario Specs + Brief Template (Foundation) ✅

**What changes:**
- Drop brief template gets a mandatory `## Scenarios` section
- Scenarios follow Given/When/Then/Verify format
- Verify clauses are machine-executable where possible (shell commands, curl, duckdb queries)
- Interview protocol adds scenario extraction as a required step

**Files to modify:**
1. `Skills/pulse/references/drop-brief-template.md` — Add `## Scenarios` section between Requirements and Success Criteria. Scenarios are the *primary* acceptance mechanism; Success Criteria becomes secondary (structural checks).
2. `Skills/pulse/references/interview-protocol.md` — Add Question 7: "What are the behavioral scenarios?" with guidance on writing Given/When/Then/Verify.
3. `Skills/pulse/scripts/pulse.py` (validate command) — Add check: Drop briefs without `## Scenarios` section trigger a warning.

**Template for scenario section:**
```markdown
## Scenarios

<!-- Behavioral acceptance criteria. Each scenario describes an observable outcome.
     Verify clauses should be executable commands when possible. -->

S1: <Descriptive name>
  Given: <Initial state or precondition>
  When: <Action or trigger>
  Then: <Expected observable outcome>
  Verify: <Command or check that confirms the outcome>

S2: <Edge case or alternative path>
  Given: ...
  When: ...
  Then: ...
  Verify: ...
```

**Success criteria for Phase 1:**
- Drop brief template includes Scenarios section with clear instructions
- Interview protocol extracts scenarios before planning begins
- Validate command warns on missing scenarios
- At least one real build uses the new template successfully

---

## Phase 2: Spec-Writing Skill (Address Root Bottleneck) ✅

**What changes:**
- New skill at `Skills/spec-writing/` that runs a structured interview to extract scenarios, edge cases, and acceptance criteria from rough intent
- Integrates with existing `pulse-interview` flow — spec-writing runs *before* Architect planning
- Outputs a spec artifact that the Architect consumes

**Files to create:**
1. `Skills/spec-writing/SKILL.md` — Skill definition
2. `Skills/spec-writing/references/scenario-patterns.md` — Common scenario patterns by build type (API, data pipeline, frontend, integration, hotline/webhook)

**Skill workflow:**
```
V says: "I want to build X"
  → Spec-writing skill activates
  → Structured interview: what, who uses it, happy path, sad paths, edge cases
  → Generates: scenario list + identified ambiguities + decision points
  → V reviews and approves scenarios
  → Architect receives approved scenarios as input to PLAN.md
```

**Key design choice:** This skill is persona-agnostic. It runs in Operator or Architect mode. It doesn't write code or plan — it only extracts and structures intent into scenarios.

**Relationship to existing pulse-interview:**
- pulse-interview (6 questions) focuses on *decomposition* — streams, waves, dependencies
- spec-writing focuses on *validation* — what does "working" look like?
- They run in sequence: spec-writing → pulse-interview → Architect plans

**Success criteria for Phase 2:**
- Skill exists with SKILL.md and reference docs
- Running the skill on a real intent produces usable scenarios
- Architect persona instructions reference spec-writing as prerequisite

---

## Phase 3: Scenario-Based Filter (Behavioral Validation) ✅

**What changes:**
- Filter evaluates deposits against scenarios (not just structural Success Criteria)
- Each scenario gets an individual score
- Overall satisfaction score replaces boolean PASS/FAIL

**Files to modify:**
1. `Skills/pulse/references/filter-criteria.md` — Add scenario evaluation as primary rubric area (above current criteria). Scenarios are checked first; structural criteria are secondary.
2. `Skills/pulse/scripts/pulse.py` or new `pulse_scenario_filter.py` — Implement scenario-based evaluation:
   - Parse `## Scenarios` from brief
   - For each scenario with executable Verify clause: run the command, check result
   - For each scenario without executable Verify: use LLM judgment against deposit + artifacts
   - Score each scenario 0-1
   - Compute overall satisfaction as weighted average
3. Filter output schema update:
   ```json
   {
     "drop_id": "D1.1",
     "satisfaction": 0.85,
     "scenario_results": [
       {"id": "S1", "score": 1.0, "method": "command", "detail": "curl returned 200"},
       {"id": "S2", "score": 0.7, "method": "llm_judge", "detail": "Mostly correct but..."}
     ],
     "structural_results": [...],
     "verdict": "PASS",
     "retry_guidance": null
   }
   ```

**Threshold behavior (configurable in pulse_control.json):**
- satisfaction ≥ 0.9 → PASS, auto-advance
- 0.7 ≤ satisfaction < 0.9 → WARN, advance with logged concerns
- satisfaction < 0.7 → FAIL, auto-retry with scenario-specific feedback injected into brief

**Success criteria for Phase 3:**
- Filter evaluates scenarios individually with scores
- Executable Verify clauses actually run
- Retry feedback references specific failed scenarios
- At least one build uses scenario-based filtering end-to-end

---

## Phase 4: Holdout Scenarios (Prevent Gaming) ✅

**What changes:**
- New convention: `N5/builds/<slug>/holdout_scenarios/` directory
- Holdout scenarios are NOT included in Drop briefs — workers can't see them
- Filter reads both public scenarios (from briefs) and holdout scenarios (from directory)
- Holdout failures are weighted differently (they test intent, not implementation)

**Files to modify/create:**
1. `Skills/pulse/references/drop-brief-template.md` — Add note: "Additional holdout scenarios may exist that are not visible here"
2. `Skills/pulse/scripts/pulse.py` — Filter reads from `holdout_scenarios/` directory
3. Planning phase: Architect (or V) writes holdout scenarios during planning, stored separately

**Holdout scenario format:**
```yaml
# holdout_scenarios/D1.1_edge_cases.yaml
scenarios:
  - id: H1
    name: "Malformed input handling"
    given: "API receives JSON with missing required field"
    when: "POST /api/endpoint with {partial: true}"
    then: "Returns 400 with descriptive error, does not crash"
    weight: 0.5  # Lower weight than public scenarios

  - id: H2
    name: "Concurrent access"
    given: "Two requests arrive simultaneously for same resource"
    when: "Both POST within 100ms"
    then: "No data corruption, both get valid responses"
    weight: 1.0
```

**Success criteria for Phase 4:**
- Holdout directory convention established
- Filter reads and evaluates holdouts
- Holdout results appear in filter output but with distinct labeling
- Workers cannot access holdout scenarios through normal brief reading

---

## Phase 5: Shift Work Formalization + Gene Transfusion ✅

**What changes (Shift Work):**
- `meta.json` Drop schema gets `spec_completeness: full | partial | ambiguous`
- Pulse validate command enforces: `spawn_mode: auto` requires `spec_completeness: full`
- Auto Drops with partial specs get flagged as warnings

**What changes (Gene Transfusion):**
- Drop brief template gets optional `## Gene Transfusion Source` section
- Structured format: Exemplar, Relationship (fork/port/adapt), Preserve/Modify/Remove lists
- Workers instructed to read exemplar first before implementing

**Files to modify:**
1. `Skills/pulse/references/drop-brief-template.md` — Add Gene Transfusion section (optional)
2. `Skills/pulse/scripts/pulse.py` (validate) — Check spec_completeness vs spawn_mode consistency

---

## Phase 6: Pyramid Summaries (Context Management) ✅

**What changes:**
- Build planning phase generates multi-resolution context files
- `N5/builds/<slug>/context/` directory with overview + per-drop context
- Each context file has 2-word / 8-word / 32-word / full resolution levels
- Drop briefs reference their context file instead of inlining large chunks

**Files to create:**
1. `Skills/pulse/references/pyramid-summary-template.md` — Template for context files
2. Optional: `Skills/pulse/scripts/pulse_context.py` — Script that generates pyramid summaries from artifacts

**This phase is lower priority** — it helps at scale (builds with 10+ Drops) but isn't critical for the Level 4 transition.

---

## Phase 7: System-Level Integration ✅

**What changes across the system:**

### Architectural Principles
- `Personal/Knowledge/Architecture/principles/architectural_principles.md` — Add P40: "Specify Behaviorally" (scenarios over implementation checklists)
- P28 (Plans as Code) gets a scenario dimension

### Persona Instructions
- Architect persona: scenario writing is mandatory output during planning; refuse to plan if scenarios haven't been approved
- Builder persona: when executing Drops, check for Scenarios section; flag if missing
- Operator persona: route to spec-writing skill before Architect for new builds

### Rules
- New conditional rule: "When starting a Pulse build → ensure scenarios exist for all auto-spawn Drops"

### AGENTS.md
- Update workspace AGENTS.md with scenario-first validation as a build invariant

---

## Execution Strategy

**Phases 1-2 are the critical path** — they change how specs are written. Everything else builds on that foundation.

**Recommended approach:**
- Phases 1-2: Sequential, manual (V reviews each change)
- Phase 3: Could be a Pulse build itself (meta: build the better filter)
- Phases 4-7: Can be done incrementally as opportunities arise

**Total scope estimate:**
- Phase 1: ~5 files modified
- Phase 2: ~3 files created
- Phase 3: ~3 files modified/created (most complex — new evaluation logic)
- Phase 4: ~3 files modified
- Phase 5: ~2 files modified
- Phase 6: ~2 files created
- Phase 7: ~5 files modified across system

---

## What This Does NOT Change

- Pulse orchestration engine (Waves, Streams, Sentinel, recovery) — already strong
- Worker isolation model (P38) — already strong
- Audit trail (P39) — already strong
- File system as memory substrate — already strong
- Feature branching convention — already adequate

## Completion Summary

**Executed:** 2026-02-21 in conversation con_mG5yzbSSJUnMnZcK

**Files created:**
- `Skills/spec-writing/SKILL.md` — Scenario extraction skill
- `Skills/spec-writing/references/scenario-patterns.md` — Patterns by build type
- `Skills/pulse/references/holdout-scenarios-template.md` — Holdout convention
- `Skills/pulse/references/pyramid-summary-template.md` — Multi-resolution context
- `Personal/Knowledge/Architecture/principles/P40_specify_behaviorally.md` — New principle

**Files modified:**
- `Skills/pulse/references/drop-brief-template.md` — Added Scenarios, Gene Transfusion, spec_completeness
- `Skills/pulse/references/interview-protocol.md` — Added Question 7 (scenarios)
- `Skills/pulse/references/filter-criteria.md` — Scenario-based evaluation with satisfaction scoring
- `Skills/pulse/scripts/pulse_plan_validator.py` — Scenario + spec_completeness checks
- `Skills/pulse/SKILL.md` — Updated validation docs, folder structure, related files
- `Personal/Knowledge/Architecture/principles/architectural_principles.md` — Added P40

**Rules created:**
- Conditional rule: When starting Pulse build → ensure scenarios exist for auto-spawn Drops

**Open questions resolved by judgment:**
1. Scenario granularity: 3-5 per Drop (template shows 3 as minimum)
2. Holdout authorship: Architect writes during planning, V can add more
3. Filter cost: Worth it — satisfaction scoring replaces binary pass/fail
4. P40 naming: "Specify Behaviorally"
5. Test case: Next Pulse build will be the first test

## Open Questions for V

1. **Scenario granularity:** How many scenarios per Drop feels right? StrongDM uses "hundreds per hour" but they're testing products at scale. For N5OS builds, 3-5 scenarios per Drop seems right. Agree?

2. **Holdout authorship:** Should holdouts come from you during planning, or should the Architect generate them? If Architect generates them, there's a philosophical issue — the same "system" writing code is writing the hidden tests. StrongDM solves this by having scenarios live outside the codebase entirely.

3. **Filter execution cost:** Scenario-based filtering with LLM judgment per scenario will increase token spend per Drop. Currently Filter is lightweight. Worth the cost?

4. **P40 naming:** "Specify Behaviorally" — or would you prefer different language for this principle?

5. **Immediate test case:** Which upcoming build should we use as the first test of scenario-based specs?
