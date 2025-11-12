---
tool: true
description: Systematic review of completed work against principles and objectives
tags: [workflow, quality, validation, debugging]
version: 1.0
created: 2025-11-03
---

# Review Work

Systematic review of completed work to validate quality, completeness, and principle compliance.

## Instructions

**You are reviewing completed work. Be thorough and honest.**

### 1. Identify What Was Built

**Scan and catalog:**
- All files created/modified
- Scripts and their purposes
- Documentation produced
- Tests or validations run

**Output format:**
```
## Inventory
- Component 1: [path] - [purpose]
- Component 2: [path] - [purpose]
...
```

### 2. Validate Against Objectives

**Check:**
- ✅ Were original objectives met?
- ✅ Are success criteria satisfied?
- ⚠️ What's incomplete or missing?
- ❌ What explicitly failed?

**Be honest about completion (P15):**
- NOT: "✓ Done" when 70% complete
- YES: "Status: 14/20 objectives met (70%)"

### 3. Test Core Functionality

**Run actual tests:**
```
# Don't just assume it works
# Actually execute and verify

1. Happy path: [describe test] → [result]
2. Edge case: [describe test] → [result]
3. Error handling: [describe test] → [result]
```

**Evidence required:**
- Command output
- File contents
- State verification
- Error logs if failures

### 4. Check Principle Compliance

**Core principles to validate:**

**P15 - Complete Before Claiming:**
- [ ] Honest completion percentage reported
- [ ] No premature "Done" claims

**P5 - Safety & Determinism:**
- [ ] No data loss risks
- [ ] Dry-run available for destructive ops
- [ ] Backups considered

**P7 - Idempotence:**
- [ ] Can re-run safely
- [ ] Same inputs → same outputs

**P11 - Failure Modes:**
- [ ] Error handling present
- [ ] Recovery paths documented
- [ ] Logs for debugging

**P21 - Document Assumptions:**
- [ ] All placeholders documented
- [ ] Stubs explicitly marked
- [ ] Assumptions listed

**P23 - Trap Doors:**
- [ ] Irreversible decisions identified
- [ ] Alternatives considered
- [ ] Trade-offs documented

**P28 - Plan DNA:**
- [ ] Code matches plan
- [ ] Plan was clear/complete
- [ ] Upstream quality checked

### 5. Identify Issues

**Critical Issues** (blocks production use):
- 🚨 [Issue description]
- Impact: [what breaks]
- Fix: [specific action needed]

**Quality Concerns** (works but needs improvement):
- ⚠️ [Concern description]
- Why it matters: [context]
- Recommendation: [how to improve]

**Not Tested** (unknown status):
- ❓ [Component/feature]
- Why not tested: [reason]
- Risk level: [low/medium/high]

### 6. Root Cause Analysis

**If bugs found:**
```
Bug: [description]
Root cause: [why it happened]
Category:
  [ ] Missing plan
  [ ] Plan unclear
  [ ] Code doesn't match plan
  [ ] Assumptions wrong
  [ ] Dependencies missing
  [ ] Error handling absent
Prevention: [how to avoid in future]
```

### 7. Generate Review Report

**Format:**
```markdown
# Work Review: [Project Name]

## Summary
[2-3 sentence overview]

## Completion Status
- Objectives met: X/Y (Z%)
- Critical functionality: [Working/Partial/Broken]
- Production ready: [Yes/No/With caveats]

## Testing Results
- Happy path: [✓/✗]
- Edge cases: [✓/✗/Not tested]
- Error handling: [✓/✗/Not tested]

## Principle Compliance
[List principles checked with ✓/✗/⚠️]

## Issues Found
### Critical
[List or "None"]

### Quality Concerns
[List or "None"]

### Not Tested
[List or "None"]

## Recommendations
1. [Priority action]
2. [Next priority]
3. [Nice to have]

## Sign-Off
Reviewer: [Persona name]
Status: [Approved/Approved with conditions/Needs work]
Date: [timestamp]
```

---

## Quality Checks

Before delivering review:

- [ ] Actual testing performed (not assumed)
- [ ] Honest assessment (P16 - no embellishment)
- [ ] Specific issues identified with evidence
- [ ] Root causes analyzed, not just symptoms
- [ ] Actionable recommendations provided
- [ ] Completion status accurate (P15)

---

## Anti-Patterns

**❌ Rubber-stamp approval**
"Everything looks good!" without actually testing

**❌ Vague criticism**
"Code quality could be better" without specifics

**❌ Assuming functionality**
"Should work" without running tests

**❌ Missing root cause**
"Bug found" without analyzing why it happened

**❌ False completion**
"✓ Review complete" when only 60% checked

---

## Related

- Principles: P15 (Complete Before Claiming)
- Principles: P16 (Accuracy Over Sophistication)
- Principles: P11 (Failure Modes)
- Persona: Debugger (verification specialist)
- Prompt: `close-conversation.md` (often runs after review)

---

**Honest review prevents production failures.**
