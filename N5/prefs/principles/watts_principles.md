---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_fLt3MnecLZ4NGDs0
---

# Prompt Engineering Principles

## Source
Derived from Jarrod Watts' approach to AI orchestration.
Inspired by his X post about beating Anthropic's kernel challenge with zero kernel knowledge.

## Core Principle: 100x Leverage

Every word in a prompt has **100x leverage** when running agentic loops.
"Vibe coding the prompt was not good enough."

When a prompt runs through a loop (like Pulse spawning Drops),:
- A vague instruction gets executed repeatedly
- Ambiguity compounds across iterations
- Quality gates fail silently
- Time and compute are wasted on dead ends

The cost of a bad prompt is multiplied by the number of agents using it.

## Anti-Patterns (Never Use)

| Pattern | Problem | Instead |
|---------|---------|---------|
| `"try to X"` | Permits failure | `"X"` or `"X, or escalate if blocked"` |
| `"if possible"` | Permits skipping | `"X unless [condition]"` or specify the condition |
| `"maybe/perhaps"` | Ambiguous intent | Be definitive or remove the speculation |
| `"improve X"` | No target to aim for | `"improve X by Y%"` or `"improve X until [metric] reaches [target]"` |
| `"optimize"` | No success criteria | `"optimize until [metric] reaches [target]"` |
| `"etc.", "and so on"` | Incomplete specification | List all items explicitly |
| `"as needed"` | Undefined trigger | Specify when action is needed |
| `"soon", "quickly"` | Vague timing | Specify timeframe: `"within 5 minutes"` |
| `"good", "better"` | Subjective quality | Define measurable criteria |
| `"some", "few", "many"` | Vague quantity | Use specific numbers |
| Passive voice (`"was improved by"`) | Unclear actor | Use active voice: `"X improved Y"` |
| `"should"` | Weak requirement | Use `"must"` for requirements |

## Required Sections in Drop Briefs

Every Drop brief must have these sections:

### 1. Objective
- **Single sentence** describing what success looks like
- Clear, measurable outcome
- Example: `"Create a CLI tool that scans deposits for contradictions"`

### 2. Context
- Why this task matters
- What came before (dependencies)
- How it fits into the larger build
- Example: `"D2.1 created impossibility detector. D2.2 needs to use it for contradiction detection."`

### 3. Requirements
- **Numbered list** of specific tasks
- Each requirement must be:
  - Measurable (you can tell if it's done)
  - Action-oriented (not `"consider X"`)
  - Unambiguous (not `"if possible"`)
- Example:
  ```
  1. Import impossibility_detector module
  2. Implement check_before_adding() function
  3. Return dict with can_add boolean
  ```

### 4. Success Criteria
- **Checklist of verifiable outcomes**
- Binary: either achieved or not
- Example:
  ```
  - [ ] Script runs without errors
  - [ ] Import test passes
  - [ ] Integration function documented
  ```

### 5. Constraints
- What NOT to do
- Boundaries and scope limits
- Example:
  ```
  - Do not modify existing detector logic
  - Do not use external APIs beyond /zo/ask
  - Must preserve existing learnings migration
  ```

## Contamination Prevention

### Never Document "Impossible" Without Human Review
- Ceiling beliefs ("this is impossible", "can't be done") are dangerous
- They block exploration of valid approaches
- Use `impossibility_audit.py` to scan for these before builds

### Learnings Expire
- System learnings expire after 30 days if not validated
- Use `pulse_learnings.py validate` to boost confidence
- Stale learnings are marked as `expired` automatically

### Contradictions Are Flagged, Not Silently Overwritten
- Adding a learning that contradicts existing ones requires review
- `contradiction_detector.py` checks before adding
- Use `--force` only after verifying which is correct

### Fresh Context When Inherited Beliefs May Be Wrong
- System context evolves (APIs change, patterns shift)
- Learnings with high confidence may still be wrong in new contexts
- Always inject relevant learnings as "context to consider", not "absolute truth"

## Plateau Response

When a Drop is stuck (making repeated similar attempts without progress):
1. **DO NOT** just retry with the same approach
2. **CHANGE THE TOOLING**:
   - Add instrumentation/logging to identify bottleneck
   - Try a different algorithm, library, or method
   - Expand search space or adjust parameters
   - Reframe the problem entirely

The `plateau_detector.py` monitors for:
- Spinning in task attempts (high similarity between attempts)
- No meaningful progress in deposit submissions
- Error loops (same error repeatedly)

When plateaued, it suggests specific tooling changes via SMS.

## Lint Scores

The `prompt_lint.py` CLI enforces these principles:

| Score | Threshold | Meaning |
|--------|-----------|---------|
| 90-100 | ready | Ready to use, no issues |
| 70-89 | acceptable | Minor issues, consider fixes |
| 50-69 | needs_attention | High-severity issues present |
| 0-49 | rewrite | Rewrite recommended |

Severity levels:
- **High**: Blocks spawn (score penalty: 15 points each)
  - "try to", "if possible", vague improvements
- **Medium**: Warnings (score penalty: 5 points each)
  - Passive voice, weak requirements, subjective terms
- **Low**: Suggestions (score penalty: 1 point each)
  - Long sentences, minor style issues

## Safety Checks (Pre-Build)

Before any build starts, Pulse runs:

1. **Impossibility Audit** (`impossibility_audit.py`)
   - Scans SYSTEM_LEARNINGS.json for ceiling beliefs
   - Scans deposits and BUILD_LESSONS for impossibility claims
   - High-severity findings **block** the build

2. **Prompt Lint** (`prompt_lint.py`)
   - Lints all Drop briefs
   - Score < 70 **blocks** the build
   - Scores 70-89 show warnings

If safety checks fail:
- Build status set to `blocked`
- SMS sent to V with blockers
- Build does not proceed until resolved

## Sentinel Monitoring (During Build)

While Drops are running, Sentinel checks:

1. **Dead Drops**: No deposit for 15 minutes → SMS escalation
2. **Plateaued Drops**: Spinning without progress → SMS with tooling suggestions
   - Only alerts once per Drop per 10 minutes (no spam)
   - Suggests: retry/skip/reframe with specific tooling advice

## Learning Addition Flow

When adding a learning via `pulse_learnings.py add`:

1. **Contradiction Check** (`contradiction_detector.py`)
   - Scans existing system learnings
   - High similarity + contradiction signals → blocks addition
   - Medium confidence → warns and requests review

2. **If blocked**:
   - Shows conflicting learnings
   - Shows similarity scores and contradiction confidence
   - Requires `--force` to override (after verifying)

## Quick Reference

For Drop briefs:
- ✅ Do: Use definitive language, measurable criteria
- ❌ Don't: Use tentative language, vague targets

For learning additions:
- ✅ Do: Check for contradictions before adding
- ❌ Don't: Overwrite existing learnings blindly

For stuck Drops:
- ✅ Do: Change tooling, add instrumentation
- ❌ Don't: Just retry with same approach

For builds:
- ✅ Do: Run pre-build safety checks
- ❌ Don't: Start with contaminated state
