# Proposed Solution: AutoIndex Schema Validation Errors

**Source:** Squawk List  
**Item ID:** squawk-001  
**Priority:** HIGH  
**Status:** open  
**Generated:** 2025-10-10 00:31 ET  
**Tags:** schema, validation, indexing, critical, documentation

---

## Issue Summary

Schema validation failures in commands.jsonl are preventing automatic index updates. The indexer/validator rejects entries where command metadata fields do not conform to the current commands.schema.json contract (examples: invalid workflow values, overly long summaries, and non-string input/output type values).

### Error Details (reported)

Schema validation failed: inputs.3.type integer not in allowed types, outputs.0.type array not in allowed types, outputs.1.type integer not in allowed types

### Affected Components

- N5/scripts/n5_index_update.py
- N5/scripts/n5_index_rebuild.py
- N5/commands.jsonl
- N5/index.jsonl → N5/index.md (regeneration failure)

### Impact

Automated documentation and index generation fail; manual index updates are the current workaround. This blocks downstream automation (docgen, indexing, entrypoint detection) and increases risk of drift and data-loss when fixes are applied ad-hoc.

---

## Root Cause Analysis

Summary (non-technical): the commands registry (commands.jsonl) contains entries produced under older conventions or free-text authoring. The current JSON Schema for commands (N5/schemas/commands.schema.json) is stricter than the historical data: fields like `workflow` now accept a controlled enum, `summary` is capped at 180 characters, and `inputs[].type` / `outputs[].type` must be one of a defined set of string tokens. Several command objects violate these constraints (legacy values such as "single-shot" or "conversational", long embedded documentation in `summary`, and non-string type values). The immediate failure is schema validation during index/regeneration.

Contributing factors:
- No enforced validation on write: append/authoring paths add entries without schema enforcement.
- Schema was tightened after some commands were authored (schema drift).
- Command descriptions contain embedded long-form docs rather than referencing separate function files, causing summary length violations.

Evidence (partial): validation and remediation tooling were run and produced the attached reports:
- Validator run: /home/.z/workspaces/con_FGC5wHE5e2EInCkF/validate_commands.py → use this to reproduce.
- Proposed fixes report: /home/workspace/N5/logs/maintenance/squawk/proposed_command_fixes_2025-10-10T003635.jsonl (48 commands flagged). Example entries: `digest-runs` summary length 879 chars; many commands use `workflow: "single-shot"` which is not in the allowed enum.

---

## Proposed Solution (step-by-step)

Goal: restore automated index/docgen by bringing commands.jsonl into schema compliance, while keeping changes reversible and reviewable.

1) Audit (reproduce, evidence):
   - Run validator and save report:
     - python3 /home/.z/workspaces/con_FGC5wHE5e2EInCkF/validate_commands.py > /home/workspace/N5/logs/maintenance/squawk/validation_report_$(date +%F).txt
   - Review the generated file and the proposed fixes file: /home/workspace/N5/logs/maintenance/squawk/proposed_command_fixes_2025-10-10T003635.jsonl

2) Prepare workspace and backups (MANDATORY):
   - Create a git commit or at minimum a timestamped backup before edits:
     - cp /home/workspace/N5/commands.jsonl /home/workspace/N5/commands.jsonl.squawk-001.preapply.bak
     - git add /home/workspace/N5/commands.jsonl && git commit -m "chore: backup commands.jsonl before squawk-001 remediation"

3) Review suggested changes (manual approval step):
   - The proposed fixes file contains one entry per flagged command and suggested normalized values (workflow mapping, truncated summaries, normalized input/output types). Open and review it:
     - less /home/workspace/N5/logs/maintenance/squawk/proposed_command_fixes_2025-10-10T003635.jsonl
   - Decision: approve the set of automated normalizations, or select a subset to apply manually.

4) Apply fixes in dry-run to a copy (no production overwrite):
   - Copy registry for testing:
     - cp /home/workspace/N5/commands.jsonl /home/workspace/N5/commands.jsonl.squawk-001.test.jsonl
   - Run an application script (not applied here until you approve) that consumes the proposed fixes report and produces a fixed file at `/home/workspace/N5/commands.jsonl.fixed`.
   - Validate the fixed file with the same validator until it reports no schema errors.

5) If tests pass, apply atomically with versioned backup and git commit:
   - mv /home/workspace/N5/commands.jsonl /home/workspace/N5/commands.jsonl.squawk-001.preapply.bak
   - mv /home/workspace/N5/commands.jsonl.fixed /home/workspace/N5/commands.jsonl
   - git add N5/commands.jsonl && git commit -m "fix(commands.jsonl): normalize fields to schema (squawk-001)"

6) Regenerate index and verify downstream systems:
   - python3 /home/workspace/N5/scripts/n5_index_rebuild.py --dry-run (or without --dry-run after approval)
   - Confirm /home/workspace/N5/index.jsonl and /home/workspace/N5/index.md regenerate cleanly and that docgen runs without schema errors.

7) Prevent regression (post-merge hardening):
   - Add pre-commit / CI validation that runs the same jsonschema check against commands.jsonl and rejects changes that fail validation.
   - Update append_command.py (and any authoring paths) to run validation before append; block writes on validation failure and provide human-facing error with suggested fix.

Files and scripts produced during this task (already created for review):
- Validator: /home/.z/workspaces/con_FGC5wHE5e2EInCkF/validate_commands.py
- Proposed-fixes generator (dry-run): /home/.z/workspaces/con_FGC5wHE5e2EInCkF/propose_command_fixes.py
- Proposed-fixes report: /home/workspace/N5/logs/maintenance/squawk/proposed_command_fixes_2025-10-10T003635.jsonl

---

## Risk Assessment

High-level risks:
- Incorrect automated mappings may change semantics (e.g., mapping `workflow` to the wrong bucket) and break tooling that relies on the original value.
- Truncating `summary` may remove important information used by humans; automated truncation must preserve the full text elsewhere (function_file or backups).
- Automated type normalizations (e.g., converting numeric type values to string tokens) may be lossy if the original intent differs.

Mitigations:
- Always operate on a copy and produce a fixed candidate file for review.
- Keep timestamped backups and git commits for immediate rollback.
- Require explicit human approval before writing the canonical commands.jsonl (do not auto-apply).
- Add unit/validation checks and smoke tests (index regenerate, docgen, sample command run) after applying changes.

Reversibility:
- Changes are reversible by restoring the preapply backup or by git revert. A backup copy is created automatically as part of the steps above.

---

## Test Validation Steps (concrete)

1) Pre-implementation verification:
   - [ ] Run validator: python3 /home/.z/workspaces/con_FGC5wHE5e2EInCkF/validate_commands.py and save output.
   - [ ] Confirm the proposed fixes file exists and inspect the top 10 flagged items.

2) Post-implementation verification (after applying to test copy):
   - [ ] Run validator against /home/workspace/N5/commands.jsonl.fixed — should return no schema errors.
   - [ ] Run index rebuild: python3 /home/workspace/N5/scripts/n5_index_rebuild.py --dry-run and confirm no validation exceptions.
   - [ ] Regenerate MD view: python3 /home/workspace/N5/scripts/n5_index_rebuild.py (if safe) and confirm /home/workspace/N5/index.md updated.

3) Integration checks:
   - [ ] Run docgen (or docgen dry-run) to confirm command documentation generation completes.
   - [ ] Spot-check 3 representative commands (one from lists, one from knowledge, one from ops): run their help/usage paths and confirm expected metadata present.

---

## Rollback Procedure

If the applied change causes issues:

1) Immediate rollback (fastest):

```bash
# Restore backup made before apply
cp /home/workspace/N5/commands.jsonl.squawk-001.preapply.bak /home/workspace/N5/commands.jsonl
# Rebuild index
python3 /home/workspace/N5/scripts/n5_index_rebuild.py --dry-run
```

2) Git-based rollback (preferred if changes were committed):

```bash
# Revert the commit that applied the fixed file
git revert <commit-hash>
# Or reset to previous commit if appropriate
git reset --hard HEAD~1
```

3) Verification after rollback:
- Run validator and index rebuild to confirm system returns to prior state.

---

## Clarifying Questions (please answer when you review)

1) Workflow mapping preference: when suggested mappings are presented (e.g., `single-shot` → `ops`, `conversational` → `automation`), do you approve those defaults or should we present a per-command mapping for your review?
2) Summary handling: do you want long summaries truncated to 180 chars with the remainder moved into the command's `function_file` (commands/*.md), or should we instead relax the schema to allow longer summaries for now?
3) Inputs/Outputs types: for non-string type values should we automatically normalize (numeric→"integer", array→first-string or "json") or flag them for manual correction?
4) Deployment policy: after fixes, should we (A) apply changes automatically and commit, or (B) create a candidate fixed file for manual review and only apply after your explicit APPROVED confirmation? (Recommended: B)
5) CI enforcement: do you want a pre-commit hook and CI check added immediately to prevent recurrence? (Recommended: yes)

---

## Implementation Checklist

- [ ] Review validation and proposed fixes reports: /home/workspace/N5/logs/maintenance/squawk/proposed_command_fixes_2025-10-10T003635.jsonl
- [ ] Answer clarifying questions above
- [ ] Approve remediation plan (dry-run first)
- [ ] Create backup and candidate fixed file
- [ ] Run validation and index/regeneration smoke tests
- [ ] Apply to production commands.jsonl and commit
- [ ] Add pre-commit/CI validation to enforce schema
- [ ] Close squawk-001 and document changes in timeline

---

## Notes

- I produced two tooling artifacts to assist: validator and proposed-fixes generator (dry-run). They are intentionally non-destructive and placed in the conversation workspace and N5 logs for review.
- When you approve, I will prepare an explicit apply script and perform the fixes atomically with backups and a git commit. I will NOT modify N5/commands.jsonl without your explicit APPROVED confirmation.

