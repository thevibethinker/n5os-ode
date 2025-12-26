---
created: 2025-12-14
last_edited: 2025-12-14
version: 1.0
type: build_plan
status: complete
---

# Plan: Planning System v1

**Objective:** Upgrade N5 build process to mandate Architect-owned planning with standardized plan files, auto-initialized build workspaces, and Level Upper divergent thinking integration.

**Trigger:** V's directive to elevate build quality by incorporating Ben Guo's planning prompt as baseline approach.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention. Structure everything so AI can follow autonomously.

**Level Upper Experiment:** Divergent thinking integration is experimental. We'll evaluate whether it adds value based on this build.

---

## Open Questions

- [x] Where should plan template live? → `N5/templates/build/plan_template.md`
- [x] Should Level Upper be invoked automatically or on-demand? → **Automatically** as step in Architect's planning flow
- [ ] Should existing builds be migrated to new format? → Defer (grandfather existing)

---

## Checklist

### Phase 1: Foundation (Templates + Scripts)
- ☑ Create `N5/templates/build/` directory structure
- ☑ Create `plan_template.md` with Ben's exact format
- ☑ Create `init_build.py` script for workspace auto-initialization
- ☑ Test: `python3 N5/scripts/init_build.py test-build` creates correct structure

### Phase 2: Architect Persona Upgrade
- ☑ Upgrade Vibe Architect to v3.0 in live persona
- ☑ Add plan ownership, mandatory invocation, Level Upper integration
- ☑ Update `Documents/System/personas/vibe_architect_persona.md` reference doc
- ☐ Test: Architect creates plan following template (deferred to next build)

### Phase 3: Builder Persona + Routing Updates
- ☑ Add plan gating to Vibe Builder persona (v3.1)
- ☑ Update `N5/prefs/system/persona_routing_contract.md` to mandate Architect (v1.1)
- ☑ Added Build Planning Protocol (Section 7.1)
- ☐ Test: Builder refuses to execute without valid plan (deferred to next build)

### Phase 4: Level Upper Integration
- ☑ Add divergent thinking step to Architect workflow (in Architect v3.0)
- ☑ Define Level Upper's "counterintuitive lens" prompting
- ☑ Update Level Upper persona with planning-phase role (v2.1)
- ☑ Test: Level Upper provided suggestions during THIS build's planning phase

### Phase 5: Documentation + Cleanup
- ☐ Update `N5/prefs/operations/planning_prompt.md` with plan file spec (deferred)
- ☐ Update `Prompts/pre-build-checklist.prompt.md` to reference new flow (deferred)
- ☑ Create `N5/docs/BUILD_PLANNING_GUIDE.md` quick reference
- ☑ Stored reasoning pattern: `Knowledge/reasoning-patterns/enforcement-at-execution.md`
- ☑ Archive this build with learnings

---

## Phase 1: Foundation (Templates + Scripts)

### Affected Files
- `N5/templates/build/plan_template.md` - CREATE - standardized plan format
- `N5/templates/build/status_template.md` - CREATE - build status tracking
- `N5/scripts/init_build.py` - CREATE - workspace initializer

### Changes

**1.1 Create directory structure:**
```
N5/templates/build/
├── plan_template.md      # Ben's format
├── status_template.md    # Progress tracking
└── README.md             # Usage guide
```

**1.2 Plan template follows Ben's exact structure:**
- Open questions at TOP (flagged first)
- Checklist organized by phase with ☐/☑
- Each phase has: Affected Files, Changes, Unit Tests
- No exploration steps (research done before plan)
- No backwards compatibility shims
- No concluding errata

**1.3 init_build.py features:**
- Creates `N5/builds/<slug>/` directory
- Copies plan template as `PLAN.md`
- Creates `STATUS.md` from status template
- Creates `.n5protected` marker
- Returns absolute path for conversation reference
- Validates slug (lowercase, hyphens only)

### Unit Tests
- `init_build.py test-build` creates `N5/builds/test-build/` with correct files
- Plan template contains all required sections
- Status template has progress tracking fields
- `.n5protected` prevents accidental deletion

---

## Phase 2: Architect Persona Upgrade

### Affected Files
- Vibe Architect persona (live, ID: `74e0a70d-398a-4337-bcab-3e5a3a9d805c`) - UPGRADE
- `Documents/System/personas/vibe_architect_persona.md` - UPDATE reference

### Changes

**2.1 Architect v3.0 Core Identity:**
```yaml
name: Vibe Architect
version: '3.0'
domain: System design, plan ownership, architectural gating
purpose: Create and own build plans; mandatory checkpoint before any major system changes
```

**2.2 Architect Responsibilities:**
1. **Plan Creation** - Creates `plan-<slug>.md` following template
2. **Nemawashi** - Explores 2-3 alternatives before recommending
3. **Trap Door Identification** - Flags irreversible decisions
4. **Open Questions** - Surfaces unknowns at TOP of plan
5. **Level Upper Invocation** - Triggers divergent thinking step
6. **Handoff** - Provides Builder with plan path + starting phase

**2.3 Mandatory Invocation Rule:**
- ALL major system changes route through Architect first
- "Major" = refactors >50 lines, schema changes, multi-file operations, new systems
- No direct Builder invocation for major work

**2.4 Level Upper Integration:**
- After drafting plan, Architect invokes Level Upper
- Level Upper applies "counterintuitive lens"
- Level Upper suggests unconventional approaches, edge cases, risks
- Architect incorporates or explicitly rejects suggestions with rationale

### Unit Tests
- Architect creates plan file in correct location
- Plan contains all required sections
- Level Upper invocation happens before plan finalization
- Handoff includes plan path and phase

---

## Phase 3: Builder Persona + Routing Updates

### Affected Files
- Vibe Builder persona (live, ID: `567cc602-060b-4251-91e7-40be591b9bc3`) - UPDATE
- Vibe Operator persona (live, ID: `90a7486f-46f9-41c9-a98c-21931fa5c5f6`) - UPDATE routing
- `N5/prefs/system/persona_routing_contract.md` - UPDATE

### Changes

**3.1 Builder Plan Gating:**
Builder's FIRST action before any implementation:
1. Verify plan file exists at `N5/builds/<slug>/PLAN.md`
2. Verify checklist exists and is at top
3. Verify affected files listed for current phase
4. Verify unit tests specified for current phase
5. If any missing → refuse and request Architect involvement

**3.2 Builder Progress Reporting:**
- Update checklist as phases complete: ☐ → ☑
- Update STATUS.md with honest progress (X/Y, Z%)
- Report blockers immediately
- No P15 violations (claiming done when incomplete)

**3.3 Operator Routing Update:**
Add to routing rules:
```
- Major builds/refactors → Architect FIRST (mandatory)
- Simple fixes (<50 lines, single file) → Builder direct (optional)
- If unclear → Architect (err toward planning)
```

**3.4 Routing Contract Update:**
Add section: "Build Planning Protocol"
- Architect is mandatory checkpoint for major work
- Plan file must exist before Builder executes
- Level Upper consulted during planning phase

### Unit Tests
- Builder rejects execution without plan file
- Builder updates checklist after phase completion
- Operator routes major builds to Architect
- Routing contract reflects new rules

---

## Phase 4: Level Upper Integration

### Affected Files
- Vibe Level Upper persona (live, ID: `76cccdcd-2709-490a-84a3-ca67c9852a82`) - UPDATE
- `Documents/System/personas/vibe_level_upper_persona.md` - UPDATE reference

### Changes

**4.1 Level Upper Planning Role:**
Add to Level Upper's identity:
```
## Planning Phase Role

When invoked by Architect during plan creation:
1. Apply "counterintuitive lens" to proposed approach
2. Ask: "What would a senior engineer with different background suggest?"
3. Identify non-obvious risks, edge cases, failure modes
4. Suggest unconventional alternatives (even if ultimately rejected)
5. Challenge assumptions that seem "obvious"
6. Provide divergent options, not just validation
```

**4.2 Counterintuitive Lens Prompting:**
Level Upper asks:
- "What if we did the opposite of this approach?"
- "What would break if we scaled this 10x?"
- "What's the laziest possible solution that still works?"
- "What would a skeptical reviewer criticize?"
- "What are we assuming that might not be true?"

**4.3 Integration Flow:**
```
Architect drafts plan
    ↓
Architect invokes Level Upper: "Review this plan with counterintuitive lens"
    ↓
Level Upper provides 2-3 unconventional suggestions/challenges
    ↓
Architect incorporates or rejects with rationale
    ↓
Final plan presented to V
```

### Unit Tests
- Level Upper provides divergent suggestions (not just validation)
- Architect documents Level Upper's input in plan
- Rejected suggestions include rationale

---

## Phase 5: Documentation + Cleanup

### Affected Files
- `N5/prefs/operations/planning_prompt.md` - UPDATE with plan file spec
- `Prompts/pre-build-checklist.prompt.md` - UPDATE to reference new flow
- `N5/docs/BUILD_PLANNING_GUIDE.md` - CREATE quick reference
- `N5/builds/planning-system-v1/BUILD_COMPLETE.md` - CREATE completion record

### Changes

**5.1 Planning Prompt Update:**
Add section on mandatory plan file format and location.

**5.2 Pre-Build Checklist Update:**
Integrate with new flow:
- Phase 0 now includes `init_build.py` invocation
- Phase 3 (PRD) now produces `PLAN.md` following template
- Add Level Upper divergent thinking step

**5.3 Quick Reference Guide:**
```markdown
# Build Planning Quick Reference

## Starting a Build
1. `python3 N5/scripts/init_build.py <slug>`
2. Architect creates plan in `N5/builds/<slug>/PLAN.md`
3. Level Upper reviews with counterintuitive lens
4. V approves plan
5. Builder executes phases

## Plan File Location
Always: `N5/builds/<slug>/PLAN.md`

## Required Sections
- Open Questions (TOP)
- Checklist (by phase, ☐/☑)
- Phases (Affected Files, Changes, Unit Tests)
```

### Unit Tests
- Documentation is consistent with implementation
- Quick reference covers common workflows
- Build completion record captures learnings

---

## Success Criteria

1. **Every major build has a plan file** at `N5/builds/<slug>/PLAN.md`
2. **Architect is invoked first** for all major system changes
3. **Level Upper provides divergent input** on every plan
4. **Builder refuses to execute** without valid plan
5. **Checklist format is consistent** across all plans
6. **Progress tracking is honest** (no P15 violations)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Over-planning for simple fixes | Define "major" threshold clearly; allow Builder direct for small fixes |
| Level Upper slows down planning | Time-box divergent thinking step; suggestions, not requirements |
| Existing builds don't conform | Grandfather existing; new standard applies going forward |
| Plan template too rigid | Allow flexibility within structure; required sections, optional depth |







