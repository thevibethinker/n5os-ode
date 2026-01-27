---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_UacHjTFMbOOcRuTX
build_slug: meeting-block-audit
build_type: analysis
---

# PLAN: Meeting Intelligence Block Quality Audit

## Context

The `Skills/meeting-ingestion/` skill was created on 2026-01-26 but its `processor.py` generates intelligence blocks using **minimal inline prompts** instead of the canonical **prompt files** in `Prompts/Blocks/`.

This resulted in "muddled and confused" blocks that lack the structured format and depth defined in the prompt specs.

**Root Cause:** The processor uses:
```python
BLOCK_DEFINITIONS = {
    "B01_DETAILED_RECAP": "Comprehensive meeting summary...",  # One-liner
    ...
}
```

Instead of loading the full prompt files like `Prompts/Blocks/Generate_B01.prompt.md` which contain detailed structure, required sections, and quality requirements.

## Objective

1. **Identify affected meetings** — Find all meetings from the past week that have low-quality blocks
2. **Quantify the damage** — How many meetings have degraded blocks vs properly generated ones?
3. **Fix the processor** — Update processor.py to use canonical prompt files
4. **Optionally regenerate** — Prepare list of meetings that need block regeneration

## Open Questions

- [ ] Were there OTHER meetings processed via the new skill before the RBV meeting?
- [ ] What's the quality threshold to determine "degraded" vs "acceptable"?

## Checklist

### Stream 1: Analysis (Parallel)
- [ ] D1.1 — Scan all meetings from Jan 19-26 and catalog block quality
- [ ] D1.2 — Git history trace: confirm processor.py never used prompt files
- [ ] D1.3 — Fix processor.py to load canonical prompts

### Stream 2: Report (Sequential after S1)
- [ ] D2.1 — Compile audit report with affected meetings list

## Phase 1: Parallel Analysis

### D1.1 — Meeting Block Quality Scan

**Scope:**
- All meetings in `Personal/Meetings/Week-of-2026-01-19/`
- All meetings in `Personal/Meetings/Inbox/`
- Check for quality signals:
  - Has YAML frontmatter with `provenance`?
  - Has proper `block_id` and `block_name` fields?
  - Has expected section headers per block type?
  - Word count > minimum threshold?

**Output:** JSON list of meetings with quality scores per block

### D1.2 — Git History + Provenance Trace

**Scope:**
- Trace git history of `Skills/meeting-ingestion/`
- Check file creation dates
- Identify conversation that created the skill
- Confirm whether prompts were ever wired in

**Output:** Timeline of skill creation and decisions

### D1.3 — Processor Fix

**Scope:**
- Update `Skills/meeting-ingestion/scripts/processor.py`
- Add function to load prompt files from `Prompts/Blocks/Generate_{block_code}.prompt.md`
- Fall back to inline definition if no prompt file exists
- Update `generate_block()` to inject transcript into loaded prompt

**Affected Files:**
- `Skills/meeting-ingestion/scripts/processor.py`

## Phase 2: Report Compilation

### D2.1 — Audit Report

**Scope:**
- Compile findings from D1.1, D1.2, D1.3
- List affected meetings by priority
- Recommend which meetings need regeneration
- Document the fix applied

**Output:** `N5/builds/meeting-block-audit/AUDIT_REPORT.md`

## Success Criteria

- [ ] All meetings from Jan 19-26 cataloged with quality scores
- [ ] Root cause confirmed with evidence
- [ ] Processor fixed to use canonical prompts
- [ ] Audit report generated with action recommendations
