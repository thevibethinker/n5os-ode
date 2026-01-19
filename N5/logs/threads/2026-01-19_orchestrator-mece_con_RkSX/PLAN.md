---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_plan
status: complete
provenance: con_RkSXGwBtKEEudYEP
---

# Plan: Build Orchestrator MECE Upgrade

**Objective:** Bake MECE (Mutually Exclusive, Collectively Exhaustive) worker division and token budget awareness into the build orchestrator, eliminating V's recurring manual instruction.

**Trigger:** V repeatedly provides the same instruction: "Ensure that you're divvying up the work in a mutually exclusive, collectively exhaustive way while minimizing the overall number of workers to the best extent that you can."

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [x] How does Claude Code / OpenCode divide work? → **RESOLVED**: Category-based delegation with explicit pre-declaration (category, reason, skills, expected outcome)
- [x] What's the realistic context budget? → **RESOLVED**: ~30% consumed by system prompt + mid-layer, so workers have ~70% of advertised context. Target 40% of total (57% of usable) for safety.
- [ ] Should we explore TOON format for worker briefs? → **DEFERRED** to future build; focus on MECE framework first

---

## Checklist

### Phase 1: MECE Framework Core
- ☑ Create `N5/prefs/operations/mece-worker-framework.md` — the canonical reference
- ☑ Create `N5/scripts/mece_validator.py` — validates worker briefs for overlap/gaps
- ☑ Test: Run validator against existing build's workers (linkedin-knowledge-extraction: 4 overlaps found)

### Phase 2: Template & Protocol Integration
- ☑ Update `N5/templates/build/worker_brief_template.md` — add MECE metadata fields
- ☑ Update `N5/templates/build/plan_template.md` — add MECE checklist section
- ☑ Update `N5/prefs/operations/orchestrator-protocol.md` — reference MECE framework
- ☐ Test: Create sample plan using updated templates

### Phase 3: Architect Persona Update
- ☑ Update Architect persona to mandate MECE validation before worker handoff
- ☑ Test: Persona updated with MECE validation step in workflow and self-check

---

## Phase 1: MECE Framework Core

### Affected Files
- `N5/prefs/operations/mece-worker-framework.md` - CREATE - Canonical MECE reference
- `N5/scripts/mece_validator.py` - CREATE - Validation script

### Changes

**1.1 Create MECE Framework Reference:**

The framework document will codify:

1. **MECE Principles**
   - **Mutually Exclusive**: No two workers touch the same scope (files, functions, responsibilities)
   - **Collectively Exhaustive**: All scope items are covered by exactly one worker
   - **Minimum Workers**: Combine work where cognitive load permits; don't over-split

2. **Wave Optimization Logic** (from OpenCode/Sisyphus research)
   - **Wave 1**: Workers with NO dependencies (can run in parallel)
   - **Wave 2+**: Workers that depend on Wave 1 outputs
   - **Critical path**: Identify longest dependency chain; minimize it

3. **Token Budget Rules** (conservative due to ~30% system overhead)
   - **Hard limit**: Worker brief + expected file reads ≤ 40% of model context
   - **Soft limit**: Target 30% to leave room for tool outputs, errors, iterations
   - **Split trigger**: If expected token load > 40%, split into multiple workers

4. **Scope Declaration Format** (inspired by Sisyphus pre-declaration)
   ```
   Worker W1.1:
   - SCOPE: [explicit list of files/functions/responsibilities]
   - MUST DO: [numbered list]
   - MUST NOT DO: [boundaries - what's explicitly excluded]
   - EXPECTED OUTPUT: [deliverables with success criteria]
   - TOKEN ESTIMATE: [brief tokens + expected file reads]
   ```

5. **Gap Check Protocol**
   - After defining all workers, list ALL scope items from the plan
   - Verify each item appears in exactly ONE worker's scope
   - Flag any items in 0 workers (gap) or 2+ workers (overlap)

**1.2 Create MECE Validator Script:**

```python
# N5/scripts/mece_validator.py
# Usage: python3 mece_validator.py <build_slug>
# Reads all worker briefs in N5/builds/<slug>/workers/
# Outputs: overlap/gap report
```

Features:
- Parse worker brief YAML frontmatter for `scope` field
- Extract scope items from brief body (files mentioned, responsibilities)
- Build scope → worker mapping
- Report: items with 0 workers (GAPS), items with 2+ workers (OVERLAPS)
- Estimate token budget per worker (brief length + file sizes)

### Unit Tests
- Create test build with intentional overlap → validator catches it
- Create test build with intentional gap → validator catches it
- Create valid MECE build → validator passes

---

## Phase 2: Template & Protocol Integration

### Affected Files
- `N5/templates/build/worker_brief_template.md` - UPDATE - Add MECE fields
- `N5/templates/build/plan_template.md` - UPDATE - Add MECE checklist
- `N5/prefs/operations/orchestrator-protocol.md` - UPDATE - Reference MECE

### Changes

**2.1 Update Worker Brief Template:**

Add to frontmatter:
```yaml
scope:
  files: []           # Explicit file paths this worker owns
  responsibilities: [] # Non-file scope items
  must_not_touch: []  # Explicit exclusions (for clarity)
token_estimate:
  brief_tokens: ~     # Filled by validator
  file_tokens: ~      # Sum of owned files
  total_pct: ~        # Percentage of context window
```

Add to body:
```markdown
## MECE Declaration

**MUST DO:**
1. [Specific, numbered actions]

**MUST NOT DO:**
- [Explicit boundaries]

**EXPECTED OUTPUT:**
- [Deliverables with verification method]
```

**2.2 Update Plan Template:**

Add MECE Validation section before Worker Briefs:
```markdown
## MECE Validation

### Scope Coverage Matrix
| Scope Item | Worker | Status |
|------------|--------|--------|
| file.py    | W1.1   | ✓      |

### Token Budget Summary
| Worker | Brief | Files | Total | Status |
|--------|-------|-------|-------|--------|
| W1.1   | 2k    | 8k    | 10k   | ✓ <40% |

### Validation Result
- [ ] `python3 N5/scripts/mece_validator.py <slug>` passes
```

**2.3 Update Orchestrator Protocol:**

Add section: "MECE Validation (MANDATORY)"
- Reference `N5/prefs/operations/mece-worker-framework.md`
- Require validator pass before launching workers
- Include V's original instruction as the "why"

### Unit Tests
- New plan using templates includes all MECE sections
- Templates render correctly with placeholders filled

---

## Phase 3: Architect Persona Update

### Affected Files
- Architect persona (via `edit_persona`) - UPDATE - Add MECE mandate

### Changes

**3.1 Update Architect Persona:**

Add to persona prompt:
```
## MECE Validation (MANDATORY)

Before handing off to Builder or generating worker briefs:
1. Run `python3 N5/scripts/mece_validator.py <slug>`
2. If validation fails, fix scope assignments before proceeding
3. Include validation output in plan's MECE Validation section

Reference: `file 'N5/prefs/operations/mece-worker-framework.md'`
```

### Unit Tests
- Architect refuses handoff when validator fails (simulated)

---

## Alternatives Considered (Nemawashi)

### Alternative 1: Fully Automated Worker Generation
**Idea:** Script that takes a plan and automatically generates worker briefs with MECE guarantees.
**Rejected:** Too magical; removes human judgment on scope boundaries. MECE is a thinking tool, not a generation tool.

### Alternative 2: Just Update the Rule
**Idea:** Add MECE requirement to existing orchestrator rule, no new files.
**Rejected:** Too implicit; V's instruction keeps recurring because there's no validator enforcing it.

### Alternative 3: Category-Based Delegation (Sisyphus-style)
**Idea:** Route workers by cognitive type (visual, strategic, quick, complex).
**Deferred:** Good idea but separate concern. MECE is about scope division; categories are about capability matching. Can layer later.

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Risk Level |
|----------|---------------|------------|
| New frontmatter schema for worker briefs | Medium - existing briefs need migration | Low |
| Validator script API | High - can change freely | Low |
| Architect persona update | High - can edit anytime | Low |

**No high-risk trap doors identified.**

---

## Success Criteria

1. **V never gives the MECE instruction again** — system enforces it
2. **`mece_validator.py` catches overlaps and gaps** — verified with test cases
3. **Architect persona refuses handoff without validation** — verified in test
4. **Templates include all MECE fields** — verified by inspection
5. **Documentation exists at canonical location** — `N5/prefs/operations/mece-worker-framework.md`

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Validator too strict, blocks valid plans | Make validator output advisory with `--strict` flag for enforcement |
| Token estimates inaccurate | Use conservative multipliers; document estimation method |
| Existing builds don't migrate | Framework is opt-in for new builds; don't retroactively break |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
*(To be filled after Level Upper review)*

### Incorporated:
*(To be filled)*

### Rejected (with rationale):
*(To be filled)*

---

## Worker Briefs

**This is a single-thread build** — no workers needed. Architect executes directly due to manageable scope (3 files created, 3 files updated).

If future expansion requires workers:
| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | MECE Framework Doc | `workers/W1.1-mece-framework.md` |
| 1 | W1.2 | MECE Validator Script | `workers/W1.2-mece-validator.md` |
| 2 | W2.1 | Template Integration | `workers/W2.1-templates.md` |

---

## Research Summary

**Sources:**
- OpenCode/Oh My Opencode (OMO) Sisyphus orchestrator
- Claude Code subagent documentation
- Existing N5 orchestrator protocol

**Key Learnings Applied:**
1. **Explicit pre-declaration** — Workers must declare SCOPE, MUST DO, MUST NOT DO, EXPECTED OUTPUT
2. **Category-aware delegation** — Different cognitive types need different handling (deferred to future)
3. **Token budget awareness** — ~30% overhead from system prompt; target 40% max per worker
4. **Validation before execution** — Don't trust; verify with tooling
