---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: agent_0dff3095-1068-4f53-a478-6f566f8164a0
---

# Reasoning Pattern: Dependency-Aware Workflow Execution

**Pattern Name:** Dependency-Aware Workflow Execution
**Category:** Workflow Orchestration  
**Extracted From:** MG-5 v2 Follow-Up Email Generation (2025-12-17)
**Confidence:** High - Validated across 386 directory scan

---

## Trigger

Downstream workflow (MG-5) attempts execution but finds prerequisite artifacts missing during discovery phase.

Specific trigger: Required intelligence block `B02_COMMITMENTS.md` not found in meetings with `[M]` state marker.

---

## Analysis Steps

### 1. Prerequisite Audit
- **Check for required files** before attempting generation
- **Map dependencies** between workflows (MG-2 → MG-5)
- **Identify which upstream workflow** creates missing artifacts

### 2. Impact Assessment
- **Count affected items** (28 meetings missing B02)
- **Classify blockers** (missing blocks, wrong state, existing artifacts)
- **Determine if execution is viable** or should be deferred

### 3. Chain-of-Causation Analysis
- **Upstream blocker:** MG-2 Meeting Intelligence Generator not run
- **Missing artifact:** B02_COMMITMENTS.md contains promises/commitments
- **Downstream impact:** MG-5 cannot generate authentic follow-ups without commitment data
- **Corrective action:** Schedule MG-2 before MG-5 in production

---

## Decision Criteria

### Execute Immediately If:
- [ ] All required artifacts present
- [ ] >80% of discovered items are actionable
- [ ] No upstream blockers identified

### Defer & Report If:
- [x] Critical artifacts missing (>20% of items)
- [x] Upstream workflow dependency identified
- [x] Clear chain of causation established

### Fail & Alert If:
- [ ] System error prevents discovery
- [ ] Required schemas malformed
- [ ] Circular dependencies detected

---

## Action Protocol

### When Deferring:
1. **Complete discovery scan** (don't abort early)
2. **Document all findings** with specific counts
3. **Identify dependency chain** explicitly
4. **Save completion report** with clear status
5. **Recommend execution order** for upstream workflows

### File Outputs:
- Completion report (markdown with metrics)
- Reasoning pattern extraction (this file)
- Statistics JSON for pipeline monitoring

---

## Validation Mechanisms

### Pre-Flight Checklist:
- [x] Required file templates exist in `N5/prefs/communication/`
- [x] Discovery script runs without errors
- [x] Can parse manifest.json schemas
- [x] State markers [M]/[P] are readable

### Completion Validation:
- [x] Tree scan reaches leaves (386 directories)
- [x] No meetings incorrectly skipped
- [x] All skip reasons documented
- [x] Dependency chain verified (MG-2 → MG-5)

---

## Metadata

**Extracted By:** MG-5 v2 Agent  
**Confidence Level:** High (validated across full tree)  
**Pattern Stability:** Stable - applicable to any workflow with prerequisites  
**Reuse Recommendation:** Use for MG-6, MG-7, and any downstream workflows

---

## Example Application

### Scenario: Next MG-5 Run
**Trigger:** MG-2 completes and generates B02 blocks  
**Action:** MG-5 scans again, finds B02 present  
**Result:** Follow-up emails generated for qualifying meetings

### Scenario: Warm Intro Generation (MG-4)
**Trigger:** B07_WARM_INTRODUCTIONS.md exists without generated email  
**Action:** Apply same dependency-aware pattern  
**Result:** Warm intro emails generated when prerequisites met

---

**Pattern ID:** DEP-WF-001  
**Version:** 1.0  
**Next Review:** After 3 workflow executions or when pattern deviates
