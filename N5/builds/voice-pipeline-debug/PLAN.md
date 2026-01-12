---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.1
provenance: con_TBnwuolXxSkp5t1D
type: build_plan
status: active
---

# Plan: Voice Pipeline Debug Cycle (Orchestrated)

**Objective:** Audit the Voice Library V2 + Voice Injection Layer end-to-end, identify correctness gaps, drift risks, and policy inconsistencies (especially Pangram), and produce patch-ready recommendations.

**Trigger:** V requested an orchestrated debug cycle after an initial audit surfaced concerns: prompt-only wiring vs runtime wiring, duplicated retrieval logic, and Pangram policy conflicts.

**Key Principle:** Scripts = mechanics; LLMs = semantics. This debug build MUST distinguish between (a) documentation/prompt wiring and (b) real runtime execution paths.

---

## Open Questions (resolve during audit)

- [ ] Are any of the writing generators actually executed via a script/runner that ignores prompt snippets (i.e., prompt-only wiring is non-operative)?
- [ ] Does the meeting pipeline have a real block-generation list (code) that currently excludes B35, despite MG-2 prompt documentation?
- [ ] Is Pangram being used as an auto-gate anywhere (auto-retry loops), contradicting the new “ad-hoc calibration” intent?

---

## Master Checklist

### Phase 1: Orchestrated Audit (Read-only)
- ☐ A. Runtime Wiring Audit (prompts vs actual runner scripts)
- ☐ B. Voice Library DB/Data Audit (sensitivity, drift, distribution)
- ☐ C. Pangram Policy Audit (auto-gate conflicts, duplicate prompts)
- ☐ D. Doc/Frontmatter Hygiene Audit (version fields, provenance, inconsistencies)
- ☐ Consolidate findings into a single “Issues & Recommendations” report

### Phase 2: Patch Plan (No code changes yet)
- ☐ For each issue: propose smallest viable patch (file + diff sketch)
- ☐ Classify each patch as: safe / medium risk / trap door
- ☐ Provide execution-ready follow-on plan (if V approves)

---

## Phase 1: Orchestrated Audit (Read-only)

### Affected Files (Read-only)
- `N5/scripts/voice_layer.py`
- `N5/scripts/retrieve_primitives.py`
- `N5/scripts/voice_postcheck.py`
- `N5/scripts/extract_voice_primitives.py`
- `Prompts/Follow-Up Email Generator.prompt.md`
- `Prompts/Blurb-Generator.prompt.md`
- `Prompts/X Thought Leader.prompt.md`
- `Prompts/Social Post Generate Multi Angle.prompt.md`
- `Prompts/Generate With Voice.prompt.md`
- `Prompts/Pangram Check.prompt.md`
- `Prompts/Pangram.prompt.md`
- `Prompts/Meeting Intelligence Generator.prompt.md`
- Meeting runner scripts under `N5/scripts/meeting_*` (discovered during audit)

### Worker Outputs (write reports here)
- `N5/builds/voice-pipeline-debug/worker_outputs/`

### Unit Tests / Proofs (audit proofs)
- “Runtime wiring evidence”: exact file paths + grep lines showing whether the injection layer is called in the true execution code path.
- “Meeting pipeline evidence”: locate the actual block list in code (if any) and show whether B35 is included.
- “Pangram policy evidence”: list all auto-gate language and where it lives.

---

## Phase 2: Patch Plan (No code changes yet)

### Deliverables
- `N5/builds/voice-pipeline-debug/REPORT.md` (single consolidated report)
- `N5/builds/voice-pipeline-debug/PATCH_PLAN.md` (patch-ready plan, not executed)

### Success Criteria
1. We can name the real runtime entrypoints for each generator (email, blurb, X, social post) and show whether voice injection is truly applied.
2. We can confirm whether B35 generation is operational in the meeting pipeline or only documented.
3. We produce a prioritized list of issues with patch-ready recommendations and risk classification.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Mistaking prompt documentation for real behavior | Require “runtime evidence” (script entrypoint + callsite) for each claim |
| Scope creep into implementation | Phase 1 is read-only; Phase 2 produces patch plan only |
| Overconfident conclusions | Each issue must include proof links (file path + grep excerpt) |

---

## Nemawashi (Alternatives Considered)

1. **Single-thread manual audit** (rejected): too easy to miss runtime entrypoints.
2. **Auto-apply fixes immediately** (rejected): violates safety; increases chance of breaking generators.
3. **Orchestrated audit → patch plan → V approval → execute** (chosen): maximizes correctness and control.

