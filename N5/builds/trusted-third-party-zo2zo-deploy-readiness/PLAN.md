---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.1
type: build_plan
status: active
---

# Plan: Trusted Third-Party Zo2Zo Deploy Readiness

**Objective:** Prepare and verify the trusted-third-party Zo2Zo baseline changes in `Build Exports/n5os-ode` so they are deploy-ready, then stop before commit/push for a final debug checkpoint.

**Trigger:** V asked to create a Pulse plan, get deployment-ready, and report back before committing/pushing.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [ ] Final deployment target confirmation (local validation only vs. immediate push-triggered deployment).
- [ ] Confirm whether to squash commits or keep granular commit history.

---

## Checklist

<!-- Concise one-liners. ☐ = pending, ☑ = complete. Zo updates as it executes. -->

### Phase 1: Governance + Build Contract
- ☑ Ensure build folder + plan + drops structure are present and compliant.
- ☑ Sync `BUILD.md` and `STATUS.md` with actual scope.
- ☑ Test: `python3 N5/scripts/build_contract_check.py trusted-third-party-zo2zo-deploy-readiness`

### Phase 2: Technical Verification of Scoped Changes
- ☑ Re-run script compile/smoke checks for trusted-third-party files in `n5os-ode`.
- ☑ Re-run positive + negative checks for `trusted_partner_preflight.py`.
- ☑ Test: command outputs match expected pass/fail behaviors.

### Phase 3: Deployment Readiness Packaging
- ☑ Validate git state and changed file list for intentional scope only.
- ☑ Prepare commit plan (message + file set) without committing.
- ☑ Test: clean, auditable staged diff preview available.

### Phase 4: Manual Hold Before Commit/Push
- ☑ Report readiness, risks, and exact commit/push commands.
- ☐ Wait for explicit go-ahead from V before commit/push.
- ☐ Test: no commit or push executed before approval.

<!-- Add more phases as needed. Keep to 2-4 phases that logically stack. -->

---

## Phase 1: Governance + Build Contract

### Affected Files
- `N5/builds/trusted-third-party-zo2zo-deploy-readiness/PLAN.md` - UPDATE - Convert template into executable plan
- `N5/builds/trusted-third-party-zo2zo-deploy-readiness/BUILD.md` - UPDATE - Reflect objective and next actions
- `N5/builds/trusted-third-party-zo2zo-deploy-readiness/drops/` - CREATE - Contract-compatible drop brief location
- `N5/builds/trusted-third-party-zo2zo-deploy-readiness/drops/D1-deploy-readiness.md` - CREATE - Drop brief for this execution

### Changes

**1.1 Build plan activation**
- Replace placeholders with concrete scope, checks, and stop condition.

**1.2 Contract-compatibility structure**
- Ensure drop brief path exists and contains a concrete execution brief.

### Unit Tests
- `python3 N5/scripts/build_contract_check.py trusted-third-party-zo2zo-deploy-readiness`: pass
- `ls N5/builds/trusted-third-party-zo2zo-deploy-readiness/drops`: includes `D1-deploy-readiness.md`

---

## Phase 2: Technical Verification of Scoped Changes

### Affected Files
- `Build Exports/n5os-ode/N5/scripts/conversation_sync.py` - VERIFY - behavior and CLI status path
- `Build Exports/n5os-ode/N5/scripts/trusted_partner_preflight.py` - VERIFY - pass/fail gating behavior
- `Build Exports/n5os-ode/N5/config/architectural_prefs_active.json` - VERIFY - parse/shape validity
- `Build Exports/n5os-ode/Prompts/automate-something.prompt.md` - VERIFY - frontmatter integrity
- `Build Exports/n5os-ode/Prompts/create-site.prompt.md` - VERIFY - frontmatter integrity
- `Build Exports/n5os-ode/Prompts/research-topic.prompt.md` - VERIFY - frontmatter integrity

### Changes

**2.1 Runtime checks**
- Execute direct command checks to verify expected success and expected failures.

**2.2 Syntax and structure checks**
- Compile Python files and inspect prompt/config validity.

### Unit Tests
- `python3 -m py_compile Build\ Exports/n5os-ode/N5/scripts/conversation_sync.py Build\ Exports/n5os-ode/N5/scripts/trusted_partner_preflight.py`: pass
- `python3 Build\ Exports/n5os-ode/N5/scripts/conversation_sync.py --status`: returns status without crash
- `python3 Build\ Exports/n5os-ode/N5/scripts/trusted_partner_preflight.py --repo-path Build\ Exports/n5os-ode`: pass/fail paths verified

---

## MECE Validation

<!-- 
MANDATORY for multi-worker builds.
Reference: N5/prefs/operations/mece-worker-framework.md
Run validator: python3 N5/scripts/mece_validator.py trusted-third-party-zo2zo-deploy-readiness
-->

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| Build contract + plan artifacts | W1.1 | ✓ |
| Technical verification of `n5os-ode` deltas | W1.1 | ✓ |
| Deployment-readiness packaging | W1.1 | ✓ |
| Manual hold before commit/push | W1.1 | ✓ |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~1,500 | ~10,000 | ~6% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Wave dependencies are valid (no circular, no same-wave deps)
- [ ] `python3 N5/scripts/mece_validator.py trusted-third-party-zo2zo-deploy-readiness` passes

---

## Worker Briefs

<!-- For builds using v2 orchestrator: briefs are in `workers/` folder. -->
<!-- Titles are pre-decided to enable easy thread management. -->

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Deploy Readiness + Hold Gate | `drops/D1-deploy-readiness.md` |

<!-- Add rows as needed. Wave 2+ workers depend on Wave 1 completion. -->

---

## Success Criteria

<!-- How do we know we're done? Measurable outcomes. -->
1. Build contract check passes with current artifacts.
2. Scoped trusted-third-party code changes are revalidated and deployment-ready.
3. Commit/push command set is prepared but not executed pending explicit go-ahead.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Hidden regression in trusted-party preflight logic | Re-run both positive and negative test paths before commit |
| Over-committing unintended files | Use explicit file allowlist and staged diff review before commit |
| Premature push without final debug checkpoint | Enforced Phase 4 manual hold gate |

---

## Level Upper Review

<!-- Architect invokes Level Upper before finalizing. Document the divergent input here. -->

### Counterintuitive Suggestions Received:
1. Skip Pulse and commit directly.
2. Collapse everything into one irreversible deploy step.

### Incorporated:
- Neither. Retained explicit staged verification and manual hold.

### Rejected (with rationale):
- Direct commit/push without hold: conflicts with user-requested debug checkpoint and increases rollback risk.
