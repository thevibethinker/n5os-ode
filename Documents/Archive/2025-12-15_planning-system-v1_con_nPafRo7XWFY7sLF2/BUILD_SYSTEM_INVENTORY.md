---
created: 2025-12-14
last_edited: 2025-12-14
version: 1.0
---

# N5 Build System Inventory & Gap Analysis

## Current State Summary

### Build Infrastructure Locations

| Location | Purpose | State |
|----------|---------|-------|
| `N5/builds/` | Active build workspaces | 5 builds tracked |
| `N5/scripts/build/` | Reusable build templates | 3 templates |
| `N5/prefs/operations/planning_prompt.md` | Planning discipline doc | v3.0 (comprehensive) |
| `N5/capabilities/workflows/pre-build-discovery-prd-protocol.md` | Pre-build gating protocol | v1.0 |
| `Prompts/pre-build-checklist.prompt.md` | User-invokable pre-build checklist | Active |

### Existing Builds (N5/builds/)

1. **architectural-redesign-v2/** - 30+ files, phase-tracked (p1a.md, p1b.md, etc.)
2. **cognition-layer-v1/** - WORKER_LAUNCH_MANIFEST.md pattern, 4 workers
3. **semantic-cleanup-v1/** - Single PLAN.md file
4. **mode-system-cleanup/** - Minimal
5. **orchestrator-enhancements-v1/** - Minimal

### Current Planning Artifacts

**Plan file patterns observed:**
- `PLAN.md` (semantic-cleanup-v1) - matches Ben's format fairly well
- `p1a.md`, `p1b.md`, `p2.md`... (architectural-redesign-v2) - phase-specific, fragmented
- `WORKER_LAUNCH_MANIFEST.md` (cognition-layer-v1) - worker-oriented, not phase-oriented
- No consistent `plan-<slug>.md` naming convention

**What N5 already has from Ben's principles:**
- ✅ 70% Think / 20% Review / 10% Execute framework
- ✅ Rich Hickey "Simple > Easy" principles integrated
- ✅ Nemawashi (explore 2-3 alternatives)
- ✅ Trap door identification and registry
- ✅ Squishy ↔ Deterministic spectrum guidance
- ✅ P36 (Orchestration) and P37 (Refactor) patterns
- ✅ Quality bars and self-check criteria

**What N5 is MISSING from Ben's Zo planning prompt:**
- ❌ **Mandatory `plan-<slug>.md` file convention** in project folder
- ❌ **Checklist at TOP with ☐/☑ organized by phase**
- ❌ **Affected files listed at top of each phase**
- ❌ **Unit tests inlined with relevant phases** (not separate testing section)
- ❌ **Open questions flagged at TOP of plan**
- ❌ **No exploration steps** (all research done BEFORE plan)
- ❌ **No backwards compatibility shims** (clean codebase priority)
- ❌ **No concluding errata** (future work goes in plan, not footnotes)
- ❌ **Concise one-liner checklist items** (self-consistent with plan)
- ❌ **Build workspace auto-creation** on build session start

### Persona Coverage

| Persona | Role in Build | Current State |
|---------|---------------|---------------|
| **Vibe Architect** | Creates plans, design gatekeeper | v2.0 - thin, no plan file ownership |
| **Vibe Builder** | Executes plans | v3.0 - expects plan, doesn't enforce format |
| **Vibe Debugger** | Validates builds | v3.0 - end-of-build QA |
| **Vibe Level Upper** | Quality coach for major work | Active - no planning integration |
| **Vibe Operator** | Routes, tracks state | v2.0 - routes to Builder, no plan gating |

---

## Gap Analysis: Ben's Planning Prompt vs. N5 Current State

### GAP 1: No Canonical Plan File Location or Format

**Ben's approach:**
- Plan file created in **project folder**
- Named `plan-<slug>.md`
- Specific structure: open questions → checklist → phases → affected files + tests

**N5 current:**
- Plans scattered: some in `N5/builds/<name>/`, some in project folders
- No naming convention enforced
- No template for plan file structure

**Impact:** Plans are inconsistent, hard to find, hard to track progress

### GAP 2: Architect Doesn't Own Plan Creation

**Ben's approach:**
- Planning is a distinct phase before implementation
- Plan reviewed and approved before coding starts

**N5 current:**
- Architect persona is thin (v2.0)
- Builder expects plan but doesn't enforce format
- No handoff protocol that includes plan file path

**Impact:** Plans created ad-hoc, quality varies, no gating

### GAP 3: No Build Workspace Auto-Initialization

**Ben's approach (V's request):**
- Each build session should create a dedicated workspace
- Plan files and adjacent artifacts stored consistently

**N5 current:**
- `N5/builds/<name>/` exists but created manually
- No script to initialize build workspace with template structure

**Impact:** Build hygiene depends on memory, inconsistent organization

### GAP 4: Checklist Format Not Standardized

**Ben's approach:**
- Checklist at TOP of plan
- Organized by phase
- Checkboxes: ☐ (pending) / ☑ (complete)
- Concise one-liner items

**N5 current:**
- Some plans have checklists, some don't
- Format varies (markdown checkboxes, bullet points, prose)
- Checklist often buried or missing

**Impact:** Progress tracking is manual, P15 violations more likely

### GAP 5: Unit Tests Not Inlined with Phases

**Ben's approach:**
- Each phase includes its unit tests
- Tests grouped with the code they validate
- NO separate "Testing Strategy" section

**N5 current:**
- Tests sometimes mentioned, often as afterthought
- Separate test section or none at all

**Impact:** Tests treated as optional, not integral to phase completion

---

## Recommendations (Hypotheses for Upgrade)

### H1: Create `plan-*.md` Template and Enforce It

Create `/home/workspace/N5/templates/plan_template.md` with Ben's exact structure:
```markdown
# Plan: <slug>

## Open Questions (FLAG FIRST)
- [ ] Question 1
- [ ] Question 2

## Checklist
### Phase 1: <name>
- ☐ Task 1.1
- ☐ Task 1.2

### Phase 2: <name>
- ☐ Task 2.1
...

## Phase 1: <name>

### Affected Files
- `path/to/file1.py` - <change summary>
- `path/to/file2.py` - <change summary>

### Changes
<detailed changes>

### Unit Tests
- Test A: <description>
- Test B: <description>

## Phase 2: <name>
...
```

### H2: Upgrade Vibe Architect to v3.0 as "Plan Owner"

Architect becomes the planning specialist who:
1. Creates `plan-<slug>.md` files following template
2. Applies Nemawashi (2-3 alternatives explored)
3. Identifies trap doors and flags open questions
4. Ensures Rich Hickey principles applied
5. Hands off to Builder with plan file path + phase to start

### H3: Create Build Workspace Initializer Script

`N5/scripts/init_build.py <build-name>`:
1. Creates `N5/builds/<build-name>/`
2. Copies plan template as `PLAN.md`
3. Creates `STATUS.md` (tracking file)
4. Creates `.n5protected` to prevent accidental deletion
5. Returns path for conversation reference

### H4: Add Plan Gating to Builder Persona

Builder's first action:
1. Verify plan file exists at expected location
2. Verify checklist exists and is at top
3. Verify affected files listed for current phase
4. Verify unit tests specified for current phase
5. Only then proceed with implementation

### H5: Integrate Planning into Level Upper Workflow

When Level Upper activates for major builds:
1. Check if plan exists - if not, invoke Architect first
2. Review plan quality against template
3. Monitor phase completion against checklist
4. Enforce P15 (no false completion)

---

## Proposed Build Workflow (Post-Upgrade)

```
┌──────────────────────────────────────────────────────────────┐
│ V requests build/feature                                      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Operator: Route to Architect (or Level Upper for major)       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Architect: init_build.py <slug>                               │
│ - Creates N5/builds/<slug>/                                   │
│ - Creates PLAN.md from template                               │
│ - Populates: open questions, checklist, phases, tests         │
│ - Presents plan to V for approval                             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ V approves plan (or requests changes)                         │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Builder: Execute phases sequentially                          │
│ - Verify phase prerequisites (affected files, tests)          │
│ - Implement changes                                           │
│ - Run unit tests                                              │
│ - Update checklist: ☐ → ☑                                     │
│ - Report progress honestly (X/Y, Z%)                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Debugger: End-of-build validation                             │
│ - Verify all checklist items complete                         │
│ - Run all tests                                               │
│ - Check P15 compliance                                        │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Operator: Build complete, update STATUS.md, extract learnings │
└──────────────────────────────────────────────────────────────┘
```

---

## Files to Create/Modify

| File | Action | Priority |
|------|--------|----------|
| `N5/templates/plan_template.md` | CREATE | P0 |
| `N5/scripts/init_build.py` | CREATE | P0 |
| `Documents/System/personas/vibe_architect_persona.md` | UPGRADE to v3.0 | P0 |
| `Documents/System/personas/vibe_builder_persona.md` | ADD plan gating | P1 |
| `N5/prefs/system/persona_routing_contract.md` | ADD plan requirement | P1 |
| `Prompts/pre-build-checklist.prompt.md` | INTEGRATE plan template | P1 |
| `N5/prefs/operations/planning_prompt.md` | ADD plan file spec | P2 |


