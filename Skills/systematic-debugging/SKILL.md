---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
compatibility: Created for Zo Computer
metadata:
  author: n5os-ode
  source: obra/superpowers/systematic-debugging
---

# Systematic Debugging

## The Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

Do not propose, attempt, or implement any fix until you have completed Phase 1 (Root Cause Investigation) and can articulate a specific hypothesis about *why* the bug exists. Skipping to fixes is the single most expensive debugging failure mode — it wastes time, introduces new bugs, and obscures the real problem.

---

## Phase 1: Root Cause Investigation

Before touching any code, build a complete picture of the failure.

### Steps

1. **Read the actual error** — Read the full error message, stack trace, and logs. Do not skim. Note the exact file, line, and values involved.

2. **Reproduce the failure** — Confirm you can trigger the bug reliably. If you cannot reproduce it, you do not understand it yet. Document the exact reproduction steps.

3. **Check recent changes** — What changed since this last worked? Review recent commits, config changes, dependency updates, and environment differences. The cause is almost always in what changed.

4. **Gather evidence broadly** — Before narrowing your focus:
   - Check logs at multiple levels (application, framework, system)
   - Inspect the actual data/state at the point of failure
   - Verify assumptions about inputs and environment
   - Look for related errors that may share a root cause

5. **Trace the data flow** — Follow the data from its origin to the point of failure. At each stage, verify: Is the value what you expect? Where did it come from? Where does it go next? See `references/root-cause-tracing.md` for the backward tracing technique.

### Phase 1 Exit Criteria

You can answer all of these:
- What is the exact error or unexpected behavior?
- What is the expected behavior?
- What specific input, state, or condition triggers the failure?
- Where in the code does the failure originate (not where it manifests)?

---

## Phase 2: Pattern Analysis

Find working examples to triangulate the problem.

### Steps

1. **Find a working case** — Identify a similar operation, input, or code path that *does* work correctly. If nothing similar works, that is itself a clue.

2. **Compare working vs. broken** — Diff the two cases systematically. What is different about the inputs, configuration, code path, timing, or environment?

3. **Identify the critical difference** — Narrow down to the smallest change that flips behavior from working to broken. This is often the root cause or directly adjacent to it.

4. **Understand dependencies** — Map what the broken code depends on: libraries, services, config, state, timing. Verify each dependency is behaving as expected.

---

## Phase 3: Hypothesis and Testing

Now — and only now — form a theory and test it.

### Steps

1. **Form a single hypothesis** — State it clearly: "The bug occurs because X happens when Y is in state Z." Be specific. Vague hypotheses ("something is wrong with the config") are not hypotheses.

2. **Design a minimal test** — What is the smallest change or check that would confirm or refute this hypothesis? Prefer tests that give a clear yes/no signal.

3. **Test one thing at a time** — Change exactly one variable. If you change multiple things and the bug disappears, you do not know which change fixed it (or if it is truly fixed).

4. **Verify completely** — When the hypothesis holds and the fix works:
   - Confirm the original reproduction case now passes
   - Check that related functionality still works
   - Verify no new errors in logs

---

## Phase 4: Implementation

Apply the fix with discipline.

### Steps

1. **Create a failing test first** — If feasible, write a test that captures the bug before fixing it. This prevents regression and proves you understand the failure.

2. **Make a single, focused fix** — Address only the root cause. Resist the urge to "clean up" nearby code in the same change. Unrelated changes obscure the fix and increase risk.

3. **Verify end-to-end** — Run the full test suite, not just the new test. Check logs for new warnings or errors.

4. **If 3+ fixes fail → question the architecture** — If you have attempted three or more fixes for the same issue and none have resolved it, stop. The problem is likely not where you think it is. Step back and reconsider:
   - Are you fixing a symptom instead of the cause?
   - Is the architecture itself the problem?
   - Are there hidden dependencies or state mutations you have not accounted for?
   - Would a different approach bypass the issue entirely?

---

## Red Flags

Stop and reassess if you notice any of these:

| Red Flag | What It Means |
|----------|---------------|
| Fix works "sometimes" | You have not found the real root cause; there is a timing or state dependency |
| Fix requires changing many files | Likely treating symptoms across the codebase instead of the single root cause |
| You cannot explain *why* the fix works | You do not understand the bug; the fix may be masking it |
| The same area keeps breaking | Architectural problem — patching will not help |
| You are guessing | Go back to Phase 1 |

---

## Quick Reference

| Phase | Action | Gate |
|-------|--------|------|
| 1. Root Cause | Read error → Reproduce → Check changes → Gather evidence → Trace data | Can state exact cause location |
| 2. Pattern | Find working example → Compare → Identify critical difference | Know what is different |
| 3. Hypothesis | State hypothesis → Minimal test → One change only → Verify | Hypothesis confirmed |
| 4. Implement | Failing test → Single fix → Full verification → Architecture check at 3 failures | Bug resolved, no regressions |

---

## Common Rationalizations (And Why They Are Wrong)

| Rationalization | Reality |
|-----------------|---------|
| "I know what the problem is" | Then Phase 1 should take 30 seconds. Do it anyway. |
| "Let me just try this quick fix" | Quick fixes that miss root cause create two bugs: the original and the mask. |
| "The error message is obvious" | Error messages describe *symptoms*. The cause is upstream. |
| "I have seen this before" | Similar symptoms often have different causes. Verify. |
| "There is no time for investigation" | Investigation takes minutes. Chasing wrong fixes takes hours. |
| "It works on my machine" | Then the environment difference *is* the bug. Investigate it. |
