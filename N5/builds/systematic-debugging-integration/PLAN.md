---
created: '2026-02-07'
last_edited: '2026-02-07'
version: 1.0
type: build_plan
status: ready
provenance: con_wkacyZHKp1aqxMqv
---

# Plan: Systematic Debugging Integration

**Objective:** Integrate the `systematic-debugging` skill as the core methodology behind the Vibe Debugger persona and update related rules to reference it.

**Trigger:** V imported the `systematic-debugging` skill from obra's superpowers and wants to embed it deeply into the N5 system as the authoritative debugging methodology.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved during planning -->
- [x] Should the skill replace or augment the Debugger persona? → **Augment** - persona loads and follows skill
- [x] Should the existing repeated-bugs rule be updated? → **Yes** - reference skill explicitly
- [x] Should the missing reference files (root-cause-tracing.md, etc.) be created? → **Yes** - complete the skill

---

## Checklist

### Phase 1: Complete the Skill
- ☐ Create `Skills/systematic-debugging/references/root-cause-tracing.md`
- ☐ Create `Skills/systematic-debugging/references/defense-in-depth.md`
- ☐ Create `Skills/systematic-debugging/references/condition-based-waiting.md`
- ☐ Test: Files exist and are referenced correctly from SKILL.md

### Phase 2: Update Debugger Persona
- ☐ Update Vibe Debugger persona to load systematic-debugging skill on activation
- ☐ Integrate skill's 4-phase methodology into persona workflow
- ☐ Map DEBUG_LOG.jsonl discipline to skill phases
- ☐ Test: Debugger persona prompt contains skill reference

### Phase 3: Update Rules & Integration Points
- ☐ Update conditional rule cc80a90d (repeated bugs) to reference skill
- ☐ Verify Builder persona's debugging handoff references updated Debugger
- ☐ Test: Rule contains skill file reference

---

## Phase 1: Complete the Skill

### Affected Files
- `Skills/systematic-debugging/references/root-cause-tracing.md` - CREATE - backward tracing technique
- `Skills/systematic-debugging/references/defense-in-depth.md` - CREATE - multi-layer validation
- `Skills/systematic-debugging/references/condition-based-waiting.md` - CREATE - timeout replacement

### Changes

**1.1 Create root-cause-tracing.md:**
Document the backward tracing technique referenced in SKILL.md Phase 1.5. Include:
- When to use (error deep in call stack)
- The technique (trace bad values backward to source)
- Example walkthrough
- Common mistakes

**1.2 Create defense-in-depth.md:**
Document multi-layer validation post-fix. Include:
- Adding validation at multiple layers
- Preventing same class of bug from recurring
- Example patterns

**1.3 Create condition-based-waiting.md:**
Document replacing arbitrary timeouts with condition polling. Include:
- Why timeouts are fragile
- Condition polling pattern
- Examples in different contexts

### Unit Tests
- `ls Skills/systematic-debugging/references/` shows 3 new files
- `grep -l "root-cause" Skills/systematic-debugging/SKILL.md` confirms reference exists

---

## Phase 2: Update Debugger Persona

### Affected Files
- Vibe Debugger persona (ID: 17def82c-ca82-4c03-9c98-4994e79f785a) - UPDATE - add skill loading

### Changes

**2.1 Add MANDATORY skill loading section:**
At conversation start or when debugging work begins, Debugger must:
```
Load and follow: file 'Skills/systematic-debugging/SKILL.md'
```

**2.2 Map skill phases to existing workflow:**
Current Debugger protocol maps to skill as:
- Step 1 (Reproduce) → Skill Phase 1 (Root Cause Investigation)
- Step 2 (Isolate) → Skill Phase 1.4 (Gather Evidence)
- Step 3 (Hypothesize) → Skill Phase 3 (Hypothesis and Testing)
- Step 4 (Test) → Skill Phase 3.2 (Test Minimally)
- Step 5 (Fix & Verify) → Skill Phase 4 (Implementation)

**2.3 Integrate 3+ fixes escalation:**
Add to persona: If 3+ fixes fail on same issue, invoke skill's Phase 4.5 (Question Architecture) before continuing.

**2.4 Connect DEBUG_LOG.jsonl to skill phases:**
Each DEBUG_LOG entry should include which skill phase the attempt corresponds to:
- Phase: root_cause | pattern | hypothesis | implementation

### Unit Tests
- Debugger persona prompt contains `systematic-debugging/SKILL.md` reference
- Debugger persona contains "3+ fixes" escalation language

---

## Phase 3: Update Rules & Integration Points

### Affected Files
- Rule cc80a90d (repeated bugs conditional) - UPDATE - add skill reference
- N5/prefs/operations/debug-logging-auto-behavior.md - UPDATE - reference skill phases

### Changes

**3.1 Update repeated-bugs rule:**
Add to instruction:
```
Before attempting fixes, load and follow: file 'Skills/systematic-debugging/SKILL.md'

Key checkpoints:
- Phase 1: Root cause investigation BEFORE any fix
- Phase 3: One hypothesis at a time
- Phase 4: If 3+ fixes fail, question the architecture
```

**3.2 Update debug-logging-auto-behavior.md:**
Add skill phase field to log format:
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --skill-phase "root_cause|pattern|hypothesis|implementation" \
  ...existing params...
```

### Unit Tests
- `list_rules` output for cc80a90d contains "systematic-debugging"
- debug-logging-auto-behavior.md contains skill-phase reference

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Drop | Status |
|------------|------|--------|
| `references/root-cause-tracing.md` | D1.1 | ✓ |
| `references/defense-in-depth.md` | D1.1 | ✓ |
| `references/condition-based-waiting.md` | D1.1 | ✓ |
| Debugger persona update | D1.2 | ✓ |
| Repeated-bugs rule update | D1.3 | ✓ |
| debug-logging-auto-behavior.md update | D1.3 | ✓ |

### Token Budget Summary

| Drop | Brief (tokens) | Files (tokens) | Total % | Status |
|------|----------------|----------------|---------|--------|
| D1.1 | ~1,500 | ~3,000 | 2.3% | ✓ |
| D1.2 | ~1,200 | ~2,500 | 1.9% | ✓ |
| D1.3 | ~1,000 | ~2,000 | 1.5% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE drop (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All drops within 40% token budget
- [x] Wave dependencies are valid (all Wave 1 - parallel)
- [ ] `python3 N5/scripts/mece_validator.py systematic-debugging-integration` passes

---

## Drop Briefs

| Wave | Drop | Title | Brief File |
|------|------|-------|------------|
| 1 | D1.1 | Complete Skill References | `drops/D1.1-skill-references.md` |
| 1 | D1.2 | Update Debugger Persona | `drops/D1.2-debugger-persona.md` |
| 1 | D1.3 | Update Rules & Docs | `drops/D1.3-rules-docs.md` |

**Note:** All drops in Wave 1 are independent and can run in parallel.

---

## Success Criteria

1. **Skill complete:** `ls Skills/systematic-debugging/references/` shows 3 files
2. **Persona updated:** Debugger persona prompt contains `systematic-debugging/SKILL.md` reference
3. **Rule updated:** Repeated-bugs rule references the skill
4. **Integration test:** When repeatedly encountering bugs, the skill methodology is invoked

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Persona update fails (API error) | Manual retry with edit_persona tool |
| Rule update breaks existing behavior | Current rule text backed up before edit |
| Skill references duplicate SKILL.md content | References are concise techniques only, SKILL.md has methodology |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. "What if the skill should NOT be in the persona, but instead be a pre-step that any persona can invoke?"
2. "Should there be a 'debug mode' that activates across ALL personas rather than just Debugger?"

### Incorporated:
- None for now - keeping focused scope. Can expand later if pattern proves valuable.

### Rejected (with rationale):
- Cross-persona debug mode: Adds complexity. Debugger persona handles debugging; others hand off. Current routing is sufficient.
- Pre-step pattern: The skill IS invokable by any persona that reads it. Debugger just has it as default.
