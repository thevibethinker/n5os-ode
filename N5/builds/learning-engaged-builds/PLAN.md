---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
type: build_plan
status: ready
---

# Plan: Learning-Engaged Build Mode

**Objective:** Transform Pulse orchestration from throughput-optimized to learning-optimized by adding Decision Points, Learning Drops, manual-default execution, Wave Reviews, and a pedagogical AAR — while removing the deprecated regex-based teaching scripts.

**Trigger:** V identified that headless Zo mode has made builds a black box. He wants to understand not just *what* was built but *why* it was built that way, and to engage with technical decisions at every build.

**Key Design Principle:** Plans are FOR AI execution. This build modifies prompts, templates, configs, and orchestrator behavior — it is primarily a content/config build with one migration script.

---

## Open Questions

*All resolved during design phase. None remaining.*

---

## Nemawashi (Alternatives Considered)

### Alternative 1: Separate Learning Engine Script
Create a standalone Python script that analyzes plans via LLM and produces a separate LEARNING_MAP.md artifact.

**Rejected because:** Adds indirection. The Architect IS an LLM — adding Learning Landscape to the plan template is simpler (Rich Hickey: don't complect). A separate artifact creates drift between plan and learning analysis.

### Alternative 2: Keep Old Teaching Scripts, Layer New Behavior On Top
Preserve moment_generator.py et al. as a "lightweight fallback" and add the new LLM-native behavior alongside.

**Rejected because:** V explicitly chose full deprecation. Two systems doing similar things creates confusion and maintenance burden. The regex patterns in moment_generator.py are a subset of what an LLM does natively.

### Alternative 3: Build as New Skill (Skills/learning-mode/)
Package everything as a standalone Skill rather than modifying Pulse internals.

**Rejected because:** This isn't a separable capability — it's a behavioral change to how Pulse orchestrates. A Skill would just become a wrapper calling back into Pulse internals. Better to modify Pulse directly.

---

## Trap Doors

1. **Deleting N5/pulse/teaching/ is irreversible** — once the glossary.json data is migrated and scripts removed, the old system is gone.
   - **Mitigation:** Phase 1 migrates glossary data FIRST. Phase 2 removes scripts AFTER migration verified. Git history preserves everything.

2. **Changing default spawn_mode to manual affects ALL future builds** — builds will pause waiting for V if he's not engaged.
   - **Mitigation:** Rush mode override is built in Phase 3. The Learning Landscape in the plan template explicitly tags mechanical Drops as auto-spawnable. The `build_mode` field in meta.json controls the default.

---

## Checklist

### Phase 1: Foundation (Config, Schema, Migration)
- ☐ Create `N5/config/understanding_bank.json` with consolidated schema
- ☐ Write migration script to port glossary.json terms → understanding_bank.json
- ☐ Run migration, verify data integrity
- ☐ Update `Skills/pulse/config/pulse_v2_config.json`: replace `vibe_teacher` section with `learning_mode` section
- ☐ Update meta.json schema documentation with new fields (`build_mode`, `learning_landscape_generated`)
- ☐ Test: understanding_bank.json has correct schema and migrated data

### Phase 2: Deprecation (Remove Old, Clean References)
- ☐ Delete `N5/pulse/teaching/` directory entirely
- ☐ Remove teaching_manager references from `N5/pulse/review_manager.py`
- ☐ Remove teaching_manager/moment_generator references from `N5/pulse/feedback_extractor.py`
- ☐ Remove teaching_manager/moment_generator references from `N5/pulse/sms_intake.py`
- ☐ Update `N5/prefs/operations/pulse_v2_guidelines.md` glossary reference
- ☐ Update `Documents/Sharing/Pulse-V3-Spec-For-Zo.md` glossary reference
- ☐ Update Teacher persona: remove inline Technical Calibration, point to understanding_bank.json
- ☐ Test: `grep -r "teaching_manager\|moment_generator\|build_review\|glossary\.json\|N5/pulse/teaching" --include="*.py" --include="*.md" --include="*.json"` returns zero live hits (excluding builds/ archives)

### Phase 3: Templates & Prompts (The Core Behavioral Changes)
- ☐ Add Learning Landscape section to `N5/templates/build/plan_template.md`
- ☐ Create `Skills/pulse/references/learning-drop-template.md` (L-prefix Drop brief)
- ☐ Create `Skills/pulse/references/decisions-template.md` (DECISIONS.md template)
- ☐ Update `Skills/pulse/references/drop-brief-template.md`: add Technical Concepts + Decision Points sections
- ☐ Update `Skills/pulse/references/interview-protocol.md`: add learning goal question
- ☐ Update `Skills/pulse/references/filter-criteria.md`: add learning annotations eval area
- ☐ Update `Skills/pulse/references/escalation-protocol.md`: add Learning Drop + Wave Review events
- ☐ Update `Skills/pulse/SKILL.md`: add Learning-Engaged Mode orchestrator instructions
- ☐ Update `Skills/drop-close/SKILL.md`: add `concepts_exercised` to deposit schema
- ☐ Update `Skills/build-close/SKILL.md`: add Pedagogical AAR section to build close
- ☐ Update `Documents/System/personas/vibe_architect_persona.md`: add Learning Landscape generation responsibility
- ☐ Test: All templates render correctly with placeholder values

### Phase 4: Pulse Engine Changes (spawn_mode default + build_mode)
- ☐ Update `Skills/pulse/scripts/pulse.py`: default `spawn_mode` to `manual` in relevant functions
- ☐ Add `build_mode` handling: read from meta.json, pass to Drop brief generation
- ☐ Ensure rush mode override works (per-Drop, per-Wave, per-Build)
- ☐ Test: New build inits with `build_mode: "learning"` and manual spawn_mode by default

---

## Phase 1: Foundation (Config, Schema, Migration)

### Affected Files
- `N5/config/understanding_bank.json` — CREATE — consolidated knowledge tracker
- `N5/scripts/migrate_glossary.py` — CREATE — one-time migration script
- `Skills/pulse/config/pulse_v2_config.json` — UPDATE — replace vibe_teacher section

### Changes

**1.1 Create understanding_bank.json:**

Schema:
```json
{
  "version": "1.0",
  "created": "2026-02-17",
  "last_updated": "2026-02-17",
  "meta": {
    "description": "V's technical understanding tracker. Single source of truth for concept mastery.",
    "migrated_from": "N5/pulse/teaching/glossary.json"
  },
  "domains": {
    "system_architecture": { "level": "solid", "notes": "workflows, SSOT, modular design" },
    "data_structures": { "level": "solid", "notes": "JSONL, schemas, file organization" },
    "abstractions": { "level": "solid", "notes": "APIs as contracts, state management" },
    "implementation": { "level": "learning", "notes": "async/await, error handling, HTTP" },
    "developer_tooling": { "level": "learning", "notes": "git workflows, debugging, testing" },
    "low_level": { "level": "new", "notes": "memory, concurrency, networking internals" }
  },
  "concepts": [
    {
      "term": "MECE",
      "precise_name": "MECE decomposition",
      "level": "solid",
      "v_description": "non-overlapping, all-covering division",
      "first_encountered": "2026-01-24",
      "last_engaged": "2026-02-17",
      "evidence": ["pulse-v2 build: D6.1", "multiple build plans"],
      "domain": "system_architecture"
    }
  ]
}
```

Levels: `new` → `encountered` → `learning` → `familiar` → `solid` → `deep`

**1.2 Write migration script:**
- Read `N5/pulse/teaching/glossary.json`
- Map each term to understanding_bank.json `concepts` array
- Map `absorbed: true` → `level: "solid"`, `absorbed: false` → `level: "encountered"`
- Preserve `v_description`, `first_encountered`, `usage_count`
- Seed `domains` from Teacher persona Technical Calibration

**1.3 Update pulse_v2_config.json:**
Replace:
```json
"vibe_teacher": {
  "enabled": true,
  "activation_points": ["interview_complete", "plan_review", "feedback", "build_complete"],
  "glossary_path": "N5/pulse/teaching/glossary.json"
}
```
With:
```json
"learning_mode": {
  "enabled": true,
  "default_build_mode": "learning",
  "understanding_bank_path": "N5/config/understanding_bank.json",
  "friction_levels": {
    "minimal": "manual spawn, summary only",
    "standard": "manual spawn, decision points, wave reviews",
    "full": "manual spawn, decision points, wave reviews, learning drops, pedagogical AAR"
  },
  "default_friction": "standard"
}
```

### Unit Tests
- `python3 N5/scripts/migrate_glossary.py && cat N5/config/understanding_bank.json | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'concepts' in d; assert 'domains' in d; assert len(d['concepts']) >= 4; print('PASS')"` — Migration produces valid output with all terms
- `python3 -c "import json; d=json.load(open('Skills/pulse/config/pulse_v2_config.json')); assert 'learning_mode' in d; assert 'vibe_teacher' not in d; print('PASS')"` — Config updated correctly

---

## Phase 2: Deprecation (Remove Old, Clean References)

### Affected Files
- `N5/pulse/teaching/` — DELETE — entire directory
- `N5/pulse/review_manager.py` — UPDATE — remove teaching_manager call (~line 127)
- `N5/pulse/feedback_extractor.py` — UPDATE — remove teaching_manager call (~line 250)
- `N5/pulse/sms_intake.py` — UPDATE — remove teaching_manager/moment_generator calls (~lines 209, 222, 235)
- `N5/prefs/operations/pulse_v2_guidelines.md` — UPDATE — update glossary reference (~line 58)
- `Documents/Sharing/Pulse-V3-Spec-For-Zo.md` — UPDATE — update glossary reference (~line 150)
- `Documents/System/personas/vibe_teacher_persona.md` — UPDATE — remove inline Technical Calibration, replace with understanding_bank reference

### Changes

**2.1 Delete N5/pulse/teaching/ entirely:**
```bash
rm -rf N5/pulse/teaching/
```

**2.2 Clean review_manager.py:**
Remove the subprocess call to `teaching_manager.py` around line 127. Replace with a comment: `# Learning mode: teaching moments handled natively by orchestrator LLM`

**2.3 Clean feedback_extractor.py:**
Remove the subprocess call to `teaching_manager.py` around line 250. Same replacement comment.

**2.4 Clean sms_intake.py:**
Remove:
- Line ~209: subprocess call to teaching_manager
- Line ~222: `from teaching_manager import get_pending_for_sms`
- Line ~235: `from moment_generator import mark_absorbed`
Replace with comment. The "teach" and "absorbed:" SMS commands should be updated to reference understanding_bank.json directly (simple JSON read/write, no script needed).

**2.5 Update pulse_v2_guidelines.md:**
Change line 58 from referencing `N5/pulse/teaching/glossary.json` to `N5/config/understanding_bank.json`.

**2.6 Update Pulse-V3-Spec-For-Zo.md:**
Change line 150 from referencing `N5/pulse/teaching/glossary.json` to `N5/config/understanding_bank.json`.

**2.7 Update Teacher persona:**
In `Documents/System/personas/vibe_teacher_persona.md`:
- Remove the "Technical Calibration" section (V's Current Level)
- Replace with: "Read V's current level from `N5/config/understanding_bank.json` — domains section for high-level, concepts array for term-level."
- Update "Careerspan Context Files" to reference understanding_bank instead of personal-understanding.json

### Unit Tests
- `grep -rn "teaching_manager\|moment_generator\|build_review\|glossary\.json\|N5/pulse/teaching" /home/workspace --include="*.py" --include="*.md" --include="*.json" | grep -v node_modules | grep -v Trash | grep -v __pycache__ | grep -v ".zo/conversations" | grep -v "N5/builds/" | grep -v "Build Exports/" | wc -l` — returns 0
- `test ! -d N5/pulse/teaching && echo "PASS"` — directory gone
- `python3 -c "import ast; ast.parse(open('N5/pulse/review_manager.py').read()); print('PASS')"` — file still parses
- `python3 -c "import ast; ast.parse(open('N5/pulse/feedback_extractor.py').read()); print('PASS')"` — file still parses
- `python3 -c "import ast; ast.parse(open('N5/pulse/sms_intake.py').read()); print('PASS')"` — file still parses

---

## Phase 3: Templates & Prompts (The Core Behavioral Changes)

### Affected Files
- `N5/templates/build/plan_template.md` — UPDATE — add Learning Landscape section
- `Skills/pulse/references/learning-drop-template.md` — CREATE — Learning Drop brief template
- `Skills/pulse/references/decisions-template.md` — CREATE — DECISIONS.md template
- `Skills/pulse/references/drop-brief-template.md` — UPDATE — add concepts + decisions sections
- `Skills/pulse/references/interview-protocol.md` — UPDATE — add learning goal question
- `Skills/pulse/references/filter-criteria.md` — UPDATE — add learning annotations
- `Skills/pulse/references/escalation-protocol.md` — UPDATE — add learning events
- `Skills/pulse/SKILL.md` — UPDATE — add Learning-Engaged Mode section
- `Skills/drop-close/SKILL.md` — UPDATE — add concepts_exercised
- `Skills/build-close/SKILL.md` — UPDATE — add Pedagogical AAR
- `Documents/System/personas/vibe_architect_persona.md` — UPDATE — add Learning Landscape

### Changes

**3.1 Add Learning Landscape to plan_template.md:**

Insert new section between "Risks & Mitigations" and "Level Upper Review":

```markdown
## Learning Landscape

<!-- Architect generates this by analyzing plan concepts against understanding_bank.json -->

### Build Friction Recommendation
<!-- minimal | standard | full — based on build complexity and concept novelty -->
**Recommended:** {{FRICTION_LEVEL}}
**Rationale:** {{WHY}}

### Technical Concepts in This Build

| Concept | V's Current Level | Domain | Pedagogical Value |
|---------|-------------------|--------|-------------------|
| {{CONCEPT}} | {{LEVEL}} | {{DOMAIN}} | ★ High / Medium / Low |

### Decision Points

| ID | Question | Options Count | Pedagogical Value | Drop |
|----|----------|---------------|-------------------|------|
| DP-1 | {{QUESTION}} | 2-3 | ★ High / Medium | W1.1 |

### Drop Engagement Tags

| Drop | Tag | Rationale |
|------|-----|-----------|
| W1.1 | pedagogical | Involves {{CONCEPT}} V is learning |
| W1.2 | mechanical | Pure file ops, concepts V knows well |

### Suggested Learning Drops

| Concept | Trigger | Brief |
|---------|---------|-------|
| {{CONCEPT}} | If V wants deep dive during DP-1 | L1.1 |
```

**3.2 Create Learning Drop brief template:**

```markdown
---
drop_id: L<stream>.<seq>
build_slug: <slug>
spawn_mode: manual
type: learning
thread_title: "[<slug>] L<stream>.<seq>: Learn — <Concept>"
---

# Learning Drop: <Concept>

**Mission:** Help V understand <concept> well enough to make informed
decisions about <specific decision point in the build>.

**V's Current Level:** <from understanding bank>

---

## Build Context

<Why this concept matters for this build. What decisions depend on it.>

## Teaching Approach

Use Vibe Teacher methodology:
1. Start with analogy from V's domain (career coaching, Careerspan, N5)
2. Explain WHY this concept exists before HOW it works
3. Target 10-15% knowledge stretch from current level
4. Use Socratic dialogue — ask questions, let V connect dots
5. Ground examples in the actual build work, not abstractions

## Reference Materials
- Understanding Bank: `N5/config/understanding_bank.json`
- Build Plan: `N5/builds/<slug>/PLAN.md` (Learning Landscape section)

## On Completion

Write deposit to `N5/builds/<slug>/deposits/<drop_id>.json`:

{
  "drop_id": "<drop_id>",
  "type": "learning",
  "status": "complete",
  "timestamp": "<ISO timestamp>",
  "concepts_covered": ["<concept1>", "<concept2>"],
  "v_conclusions": ["<V decided X because Y>"],
  "v_preferences": ["<V prefers approach A>"],
  "understanding_update": {
    "<concept>": "<new level assessment>"
  },
  "build_relevant_insights": "<anything orchestrator should know>",
  "decisions_made": ["<any decisions V reached during learning>"]
}
```

**3.3 Create DECISIONS.md template:**

```markdown
---
created: {{DATE}}
build_slug: {{SLUG}}
---

# Decisions Log: {{TITLE}}

## Decision Points

### DP-1: {{QUESTION}}
- **Date:** {{DATE}}
- **Options Considered:**
  1. {{OPTION_A}} — {{TRADEOFF}}
  2. {{OPTION_B}} — {{TRADEOFF}}
  3. {{OPTION_C}} — {{TRADEOFF}} (if applicable)
- **V's Choice:** {{CHOICE}}
- **V's Reasoning:** {{REASONING}}
- **Concepts Involved:** {{CONCEPTS}}
- **Dialogue Rounds:** {{N}}
```

**3.4 Update drop-brief-template.md:**

Add after the "Context" section:

```markdown
## Technical Concepts

<!-- Concepts from the Learning Landscape relevant to this Drop -->
| Concept | V's Level | Decision Points |
|---------|-----------|-----------------|
| {{CONCEPT}} | {{LEVEL}} | DP-{{N}} |

## Decision Points in This Drop

<!-- Decisions V should engage with before/during execution -->
| ID | Question | Options | Pedagogical Value |
|----|----------|---------|-------------------|
| DP-{{N}} | {{QUESTION}} | {{COUNT}} | ★/Medium/Low |
```

**3.5 Update interview-protocol.md:**

Add Question 6 after the existing 5 questions:

```markdown
### 6. What should V learn from this build?
- Which concepts are new to V?
- Which decisions have the highest teaching value?
- What level of engagement does V want? (minimal / standard / full)
```

**3.6 Update filter-criteria.md:**

Add evaluation area 7:

```markdown
### 7. Learning Annotations (Advisory)
- Did the Drop capture `concepts_exercised` in its deposit?
- If the Drop involved a Decision Point, was V's choice recorded?
- If the Drop was tagged `pedagogical`, was V's engagement documented?
```

**3.7 Update escalation-protocol.md:**

Add to Escalation Events table:

```markdown
| Learning Drop ready | INFO | `[LEARN] {slug} L{x.y} ready: {concept}. Open when ready.` |
| Wave Review ready | INFO | `[REVIEW] {slug} Wave {n} complete. Review ready.` |
```

**3.8 Update SKILL.md (Pulse main):**

Add new section "Learning-Engaged Build Mode" documenting:
- Learning mode is default (`build_mode: "learning"`)
- Orchestrator responsibilities: present Decision Points, spawn Learning Drops, generate Wave Reviews
- Rush mode override: `build_mode: "rush"` in meta.json, or per-Drop/Wave override
- Manual spawn default for pedagogical Drops, auto for mechanical
- Understanding bank update at build close

**3.9 Update drop-close SKILL.md:**

Add `concepts_exercised` to the deposit schema:
```json
"concepts_exercised": ["<concept1>", "<concept2>"],
```

**3.10 Update build-close SKILL.md:**

Add Pedagogical AAR section to BUILD_AAR.md generation:
```markdown
## Pedagogical Review
- **Concepts Engaged:** [list from all deposits]
- **Decisions Made by V:** [aggregated from DECISIONS.md]
- **Understanding Updates:** [proposed level changes for understanding_bank]
- **Application Questions:** 3 Socratic questions testing build-specific understanding
- **Next Learning Frontier:** Concepts V should tackle in future builds
```

**3.11 Update Architect persona:**

Add to Planning Workflow after "Step 2: Fill Out Plan":

```markdown
### Step 2b: Generate Learning Landscape
1. Read `N5/config/understanding_bank.json` for V's current levels
2. Identify all technical concepts in the plan
3. Map concepts to V's levels
4. Flag Decision Points with pedagogical value ratings
5. Tag Drops as `pedagogical` or `mechanical`
6. Recommend friction level (minimal/standard/full)
7. Suggest Learning Drops for high-value concepts V hasn't mastered
```

### Unit Tests
- All `.md` files render valid markdown (no broken formatting)
- Learning Drop template has all required YAML frontmatter fields
- DECISIONS.md template has all required sections
- Plan template Learning Landscape section has all required sub-sections
- `grep -c "Learning Landscape" N5/templates/build/plan_template.md` — returns ≥1
- `test -f Skills/pulse/references/learning-drop-template.md && echo "PASS"` — template exists
- `test -f Skills/pulse/references/decisions-template.md && echo "PASS"` — template exists

---

## Phase 4: Pulse Engine Changes (spawn_mode default + build_mode)

### Affected Files
- `Skills/pulse/scripts/pulse.py` — UPDATE — spawn_mode default + build_mode handling

### Changes

**4.1 Default spawn_mode to manual:**

In the Drop brief generation and spawning logic, change the default:
- When `build_mode == "learning"` (default): `spawn_mode: "manual"` unless Drop is tagged `mechanical` in the Learning Landscape
- When `build_mode == "rush"`: `spawn_mode: "auto"` (current behavior)

Specifically in `get_ready_drops()` and the spawn logic: check `meta.json` for `build_mode`. If learning mode, only auto-spawn Drops explicitly tagged `mechanical`. All others get launcher files generated and V is notified.

**4.2 Add build_mode to meta.json initialization:**

In `N5/scripts/init_build.py`, add to `create_meta_json()`:
```python
"build_mode": "learning",  # Default per pulse_v2_config.json
"learning_landscape_generated": False,
```

**4.3 Rush mode override support:**

Add to pulse.py a `rush` command:
```
python3 Skills/pulse/scripts/pulse.py rush <slug> [--drop <drop_id>] [--wave <wave>]
```
- No args: sets entire build to rush mode
- `--drop`: sets specific Drop to auto spawn
- `--wave`: sets all Drops in a wave to auto spawn

### Unit Tests
- `python3 -c "from Skills.pulse.scripts.pulse import load_meta; print('PASS')"` — pulse.py still imports
- Create test build with `build_mode: "learning"` → verify manual spawn default
- Create test build with `build_mode: "rush"` → verify auto spawn default
- `python3 Skills/pulse/scripts/pulse.py rush test-slug --help` — command exists

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `N5/config/understanding_bank.json` | W1.1 | ✓ |
| `N5/scripts/migrate_glossary.py` | W1.1 | ✓ |
| `Skills/pulse/config/pulse_v2_config.json` | W1.1 | ✓ |
| `N5/pulse/teaching/` (deletion) | W1.2 | ✓ |
| `N5/pulse/review_manager.py` | W1.2 | ✓ |
| `N5/pulse/feedback_extractor.py` | W1.2 | ✓ |
| `N5/pulse/sms_intake.py` | W1.2 | ✓ |
| `N5/prefs/operations/pulse_v2_guidelines.md` | W1.2 | ✓ |
| `Documents/Sharing/Pulse-V3-Spec-For-Zo.md` | W1.2 | ✓ |
| `Documents/System/personas/vibe_teacher_persona.md` | W1.2 | ✓ |
| `N5/templates/build/plan_template.md` | W2.1 | ✓ |
| `Skills/pulse/references/learning-drop-template.md` | W2.1 | ✓ |
| `Skills/pulse/references/decisions-template.md` | W2.1 | ✓ |
| `Skills/pulse/references/drop-brief-template.md` | W2.1 | ✓ |
| `Skills/pulse/references/interview-protocol.md` | W2.1 | ✓ |
| `Skills/pulse/references/filter-criteria.md` | W2.1 | ✓ |
| `Skills/pulse/references/escalation-protocol.md` | W2.1 | ✓ |
| `Skills/pulse/SKILL.md` | W2.1 | ✓ |
| `Skills/drop-close/SKILL.md` | W2.2 | ✓ |
| `Skills/build-close/SKILL.md` | W2.2 | ✓ |
| `Documents/System/personas/vibe_architect_persona.md` | W2.2 | ✓ |
| `Skills/pulse/scripts/pulse.py` | W2.3 | ✓ |
| `N5/scripts/init_build.py` | W2.3 | ✓ |

### Token Budget Summary

| Worker | Brief (est.) | Files (est.) | Total % | Status |
|--------|-------------|--------------|---------|--------|
| W1.1 | ~2,000 | ~5,000 | ~3.5% | ✓ |
| W1.2 | ~3,000 | ~12,000 | ~7.5% | ✓ |
| W2.1 | ~4,000 | ~15,000 | ~9.5% | ✓ |
| W2.2 | ~2,500 | ~10,000 | ~6.3% | ✓ |
| W2.3 | ~2,500 | ~20,000 | ~11.3% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [ ] Wave dependencies valid — W2.* depends on W1.* completion
- [ ] `python3 N5/scripts/mece_validator.py learning-engaged-builds` passes (run after briefs created)

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Foundation: Config, Schema, Migration | `drops/D1.1-foundation.md` |
| 1 | W1.2 | Deprecation: Remove Old Teaching System | `drops/D1.2-deprecation.md` |
| 2 | W2.1 | Templates & Prompts: Pulse References | `drops/D2.1-templates-pulse.md` |
| 2 | W2.2 | Templates & Prompts: Close Skills + Architect | `drops/D2.2-templates-close-architect.md` |
| 2 | W2.3 | Pulse Engine: spawn_mode + build_mode | `drops/D2.3-pulse-engine.md` |

**Wave 1** (parallel): Foundation + Deprecation can run simultaneously — no shared files.
**Wave 2** (parallel): All three workers operate on disjoint file sets. Depends on Wave 1 completion (W2.1 needs config from W1.1; W2.2 needs Teacher persona cleaned by W1.2; W2.3 needs config from W1.1).

---

## Success Criteria

1. `understanding_bank.json` exists with all migrated terms + domain levels
2. Zero live references to deprecated teaching scripts (grep returns 0)
3. `N5/pulse/teaching/` directory does not exist
4. Plan template contains Learning Landscape section
5. Learning Drop and DECISIONS.md templates exist and are complete
6. All Pulse reference docs updated (interview, filter, escalation, drop brief)
7. pulse.py respects `build_mode: "learning"` with manual spawn default
8. init_build.py creates builds with `build_mode: "learning"` by default
9. `pulse.py rush` command works for per-Drop, per-Wave, per-Build overrides
10. All modified Python files parse without errors

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Removing teaching scripts breaks SMS "teach" / "absorbed" commands | Phase 2 replaces with direct JSON read/write in sms_intake.py |
| Manual spawn default makes builds feel slow | Rush mode override + mechanical Drop tagging + V controls via Learning Landscape |
| Understanding bank schema may need iteration | Start simple (JSON file), version field enables migration later |
| Pulse.py changes could break existing builds | Build archives in N5/builds/ are not modified; changes only affect new builds |
| Too many templates could create inconsistency | All templates share the same understanding_bank.json as SSOT |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. "Don't create a Learning Engineer — the Architect IS the Learning Engineer"
2. "The existing regex-based scripts are an anti-pattern — an LLM doing regex's job"
3. "Most of this is prompt/template changes, not new code — keep it simple"
4. "Adaptive friction by complexity, not binary learning/rush"

### Incorporated:
- All four suggestions incorporated. Learning Engineer merged into Architect. Regex scripts deprecated. Build is primarily templates/prompts. Friction levels (minimal/standard/full) replace binary toggle.

### Rejected (with rationale):
- None rejected. All Level Upper suggestions aligned with Rich Hickey principles (simple > easy, don't complect).
